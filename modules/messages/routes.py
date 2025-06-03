# modules/messages/routes.py
from flask import (
    render_template, request, redirect, url_for, session, flash
)
from extensions import db
from models import Message, User
from . import messages_bp
from extensions import socketio
from flask_socketio import join_room, leave_room, emit

# Login thì zô đc
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
        db.session.query(Message, User)  # Lấy cả object Message và User
        .join(User, 
            ((User.user_id == Message.sender_id) & (Message.sender_id != uid)) |
            ((User.user_id == Message.receiver_id) & (Message.receiver_id != uid))
        )
        .filter((Message.sender_id == uid) | (Message.receiver_id == uid))
        .order_by(Message.created_at.desc())
        .all()
    )
    # Đơn giản hóa: chỉ show message gần nhất và user đối phương
    seen = set()
    recent = []
    
    # Cho cái vòng lặp lấy tt use 
    for msg, other_user in convos:
        other_id = msg.sender_id if msg.sender_id != uid else msg.receiver_id
        if other_id not in seen:
            seen.add(other_id)
            recent.append({
                "other_id": other_id,
                "other_username": other_user.username,
                "other_avatar_url": other_user.avatar_url,  # Avatar từ User
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

# Xử lý route cho từng cuộc trò chuyện
@messages_bp.route("/<int:other_id>", methods=["GET", "POST"])
@login_required
def conversation(other_id):
    uid = session["user_id"]

    # 1. Đánh dấu các tin nhắn chưa đọc là đã đọc
    unread_msgs = Message.query.filter(
        (Message.sender_id == other_id) & 
        (Message.receiver_id == uid) & 
        (Message.is_read == False)
    ).all()
    
    # Cho nó cái is_read = True
    for msg in unread_msgs:
        msg.is_read = True
    db.session.commit()
    
    # 2. Nếu POST: gửi tin nhắn mới
    # Nếu gửi tin nhắn từ trang conversation
    if request.method == "POST":
        content = request.form.get("content").strip()
        if content:
            m = Message(sender_id=uid, receiver_id=other_id, content=content)
            db.session.add(m)
            db.session.commit()
            return redirect(url_for("messages.conversation", other_id=other_id))

    # 3. Lấy toàn bộ conversation giữa 2 người, để hiển thị nội dung chat
    # Lấy toàn conversation giữa uid và other_id, sắp theo thời gian tăng dần
    conv = Message.query.filter(
        ((Message.sender_id == uid) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == uid))
    ).order_by(Message.created_at.asc()).all()

    other_user = User.query.get_or_404(other_id)
    
    # 4. TẠO lại danh sách "Trò chuyện gần đây" giống như trong inbox()
    convos = (
        db.session.query(Message, User)
        .join(User, 
            ((User.user_id == Message.sender_id) & (Message.sender_id != uid)) |
            ((User.user_id == Message.receiver_id) & (Message.receiver_id != uid))
        )
        .filter((Message.sender_id == uid) | (Message.receiver_id == uid))
        .order_by(Message.created_at.desc())
        .all()
    )
    seen = set()
    recent = []
    
    # Duyệt qua các cuộc trò chuyện để lấy thông tin người đối diện
    # # và tin nhắn mới nhất
    for msg_obj, other_u in convos:
        other_id_loop = msg_obj.sender_id if msg_obj.sender_id != uid else msg_obj.receiver_id
        if other_id_loop not in seen:
            seen.add(other_id_loop)
            recent.append({
                "other_id": other_id_loop,
                "other_username": other_u.username,
                "other_avatar_url": other_u.avatar_url,
                "last_msg": msg_obj.content,
                "timestamp": msg_obj.created_at
            })
    
    #       
    return render_template(
        "inbox.html", 
        conversation=conv, 
        other=other_user,
        conversations=recent  # Danh sách trò chuyện gần đây
    )

# ------------------- Phần xử lý Socket.IO -------------------

# join_room quản lý client “tham gia” vào phòng chat và leave_room tương tự
def register_events(socketio):
    @socketio.on("join_room")
    def handle_join(data):
        username = data.get('username', 'Unknown')
        room = data.get('room', 'default')
        join_room(room)
        emit("message", {"msg": f"{username} vào phòng."}, to=room)

    @socketio.on("leave_room")
    def handle_leave(data):
        room = data["room"]
        leave_room(room)
        emit("message", {"msg": f"{data['username']} đã chim bay."}, to=room)

@socketio.on("send_message")
def handle_send_message(data):
    """
    Khi client gửi một tin nhắn mới. 
    Data kỳ vọng:
    {
        "sender_id": <int>,
        "receiver_id": <int>,
        "content": "<nội dung>",
        "room": "<tên_room>"
    }
    """
    sender_id = data.get("sender_id")
    receiver_id = data.get("receiver_id")
    content = data.get("content", "").strip()
    room = data.get("room")
    

    if not (sender_id and receiver_id and content and room):
        return  # nếu thiếu param, không làm gì

    # 1) Lưu vào DB
    new_msg = Message(sender_id=sender_id, receiver_id=receiver_id, content=content)
    db.session.add(new_msg)
    db.session.commit()

    # 2) Broadcast tin nhắn tới tất cả client đang ở trong room đó
    # Mình sẽ gửi về 1 object bao gồm: sender_id, content, timestamp, username của sender
    sender = User.query.get(sender_id)
    payload = {
        "sender_id": sender_id,
        "sender_username": sender.username,
        "receiver_id": receiver_id, # Người nhận tin nhắn
        "content": content,
        "created_at": new_msg.created_at.strftime("%Y-%m-%d %H:%M"),
        "message_id": new_msg.message_id,  # Để client cập nhật trạng thái riêng từng tin
        "status": "Đã gửi"
    }
    emit("receive_message", payload, room=room)

# Xử lý khi người dùng đánh dấu tin nhắn là đã đọc
@socketio.on("messages_read")
def handle_messages_read(data):
    sender_id = data.get("sender_id")   # Người gửi tin nhắn
    receiver_id = data.get("receiver_id") # Người đọc tin nhắn (hiện tại)
    room = data.get("room")
    if not (sender_id and receiver_id):
        return

    # # Khi use mở conversation, server cập nhật các tin nhắn chưa đọc thành đã đọc
    unread_msgs = Message.query.filter(
        (Message.sender_id == sender_id) & 
        (Message.receiver_id == receiver_id) & 
        (Message.is_read == False)
    ).all()
    
    seen_ids = []
    for msg in unread_msgs:
        msg.is_read = True
        seen_ids.append(msg.message_id)
        
    db.session.commit()
    

    # Emit event để các client cập nhật UI, ví dụ:
        # Emit kèm danh sách ID đã đọc
    emit("messages_read", {
        "sender_id": sender_id, # Người gửi tin nhắn
        "receiver_id": receiver_id, # Người đọc tin nhắn
        "read_message_ids": seen_ids # ID các tin nhắn đã đọc
    }, room=room)