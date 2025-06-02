# modules/messages/routes.py
from flask import (
    render_template, request, redirect, url_for, session, flash
)
from extensions import db
from models import Message, User
from . import messages_bp

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@messages_bp.route("/", methods=["GET", "POST"])
@login_required
def inbox():
    uid = session["user_id"]
    # Nếu POST: gửi tin nhắn mới
    if request.method == "POST":
        to_id = int(request.form.get("to_id"))
        content = request.form.get("content").strip()
        if to_id and content:
            new_msg = Message(
                sender_id=uid,
                receiver_id=to_id,
                content=content
            )
            db.session.add(new_msg)
            db.session.commit()
            return redirect(url_for("messages.inbox"))

    # Lấy danh sách người đã chat (distinct sender/receiver)
    # Đơn giản ta chỉ show toàn conversation, mới nhất lên đầu
    convos = (
        db.session.query(Message, User.username.label("other_username"))
        .join(User, 
              (User.user_id == Message.sender_id) & (Message.sender_id != uid) |
              (User.user_id == Message.receiver_id) & (Message.receiver_id != uid)
        )
        .filter((Message.sender_id == uid) | (Message.receiver_id == uid))
        .order_by(Message.created_at.desc())
        .all()
    )
    # Đơn giản hóa: chỉ show message gần nhất và user đối phương
    seen = set()
    recent = []
    for msg, other in convos:
        other_id = msg.sender_id if msg.sender_id != uid else msg.receiver_id
        if other_id not in seen:
            seen.add(other_id)
            recent.append({
                "other_id": other_id,
                "other_username": other,
                "last_msg": msg.content,
                "timestamp": msg.created_at
            })

    # Lấy tất cả users (để chọn gửi tin)
    all_users = User.query.filter(User.user_id != uid).all()
    return render_template(
        "inbox.html", 
        conversations=recent, 
        all_users=all_users
    )

@messages_bp.route("/<int:other_id>", methods=["GET", "POST"])
@login_required
def conversation(other_id):
    uid = session["user_id"]
    # Nếu gửi tin nhắn từ trang conversation
    if request.method == "POST":
        content = request.form.get("content").strip()
        if content:
            m = Message(sender_id=uid, receiver_id=other_id, content=content)
            db.session.add(m)
            db.session.commit()
            return redirect(url_for("messages.conversation", other_id=other_id))

    # Lấy toàn conversation giữa uid và other_id, sắp theo thời gian tăng dần
    conv = Message.query.filter(
        ((Message.sender_id == uid) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == uid))
    ).order_by(Message.created_at.asc()).all()

    other_user = User.query.get_or_404(other_id)
    return render_template(
        "inbox.html", 
        conversation=conv, 
        other=other_user
    )
