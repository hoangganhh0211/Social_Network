# modules/notifications/routes.py

from flask import Blueprint, render_template, redirect, url_for, g
from flask_login import current_user
from models import Notification
from extensions import db
from sqlalchemy import desc

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.before_app_request
def load_unread_count_and_list():
    if current_user.is_authenticated:
        latest_notifs = Notification.query.filter_by(user_id=current_user.user_id)\
                            .order_by(desc(Notification.created_at))\
                            .limit(5).all()
        unread_count = Notification.query.filter_by(user_id=current_user.user_id, is_read=False).count()
        g.latest_notifications = latest_notifs
        g.unread_notif_count = unread_count
    else:
        g.latest_notifications = []
        g.unread_notif_count = 0

# **Thêm view cho “Tất cả thông báo”**
@notifications_bp.route('/')
def all_notifications():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    all_notifs = Notification.query.filter_by(user_id=current_user.user_id)\
                    .order_by(desc(Notification.created_at)).all()
    return render_template('notifications/all.html', notifications=all_notifs)

@notifications_bp.route('/mark_read/<int:notif_id>')
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.user_id:
        abort(403)
    notif.is_read = True
    db.session.commit()
    return redirect(url_for('notifications.all_notifications'))
