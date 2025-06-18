# modules/notifications/routes.py

from flask import Blueprint, render_template, redirect, url_for, g
from flask_login import current_user
from models import Notification
from extensions import db, socketio
from sqlalchemy import desc
from flask import abort
#điều hướng thông báo
from flask import url_for

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.before_app_request
def load_unread_count_and_list():
    if current_user.is_authenticated:
        latest_notifs = Notification.query.filter_by(user_id=current_user.user_id) \
                            .order_by(desc(Notification.created_at)) \
                            .limit(5).all()
        unread_count = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count()
        g.latest_notifications = latest_notifs
        g.unread_notif_count = unread_count
    else:
        g.latest_notifications = []
        g.unread_notif_count = 0

@notifications_bp.route('/')
def all_notifications():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    all_notifs = Notification.query.filter_by(user_id=current_user.user_id) \
                    .order_by(desc(Notification.created_at)).all()
    return render_template('notifications/all.html', notifications=all_notifs)

# Route để đánh dấu thông báo là đã đọc, chuyển hướngứ
from flask import request

@notifications_bp.route('/mark_read/<int:notif_id>')
def mark_read(notif_id):
    next_url = request.args.get('next') or url_for('notifications.all_notifications')
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.user_id:
        abort(403)
    notif.is_read = True
    db.session.commit()
    return redirect(next_url)

# Helper để tạo thông báo và emit realtime
def notify_user(user_id, content, link_endpoint, notif_type='info', reference_id=None, **url_kwargs):
    # Tạo URL đích (chat)
    target = url_for(link_endpoint, _external=False, **url_kwargs)
    # Tạo URL mark_read với query next=target
    mark_link = url_for(
        'notifications.mark_read',
        notif_id=0,            # sẽ set phía dưới
        next=target,
        _external=False
    )
    # Tạo Notification mà chưa commit để lấy id
    notif = Notification(
        user_id=user_id,
        content=content,
        link=mark_link,       # tạm thời chưa đúng id
        notif_type=notif_type,
        reference_id=reference_id
    )
    db.session.add(notif)
    db.session.flush()        # để notif.notification_id có giá trị
    # Cập nhật lại link với đúng notif_id
    notif.link = url_for(
        'notifications.mark_read',
        notif_id=notif.notification_id,
        next=target,
        _external=False
    )
    db.session.commit()
    socketio.emit('new_notification', notif.to_dict(), room=f'user_{user_id}')

