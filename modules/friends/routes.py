# modules/friends/routes.py
from flask import (
    render_template, request, redirect, url_for, session, flash
)
from extensions import db
from models import Friend, User
from . import friends_bp

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@friends_bp.route("/", methods=["GET"])
@login_required
def friends_list():
    uid = session["user_id"]
    # Lấy tất cả bạn bè đã accept
    # Friend có thể lưu theo (user_id_1, user_id_2) bất kỳ thứ tự
    accepted = Friend.query.filter(
        ((Friend.user_id_1 == uid) | (Friend.user_id_2 == uid)) &
        (Friend.status == "accepted")
    ).all()

    friends_objs = []
    for f in accepted:
        friend_id = f.user_id_2 if f.user_id_1 == uid else f.user_id_1
        friends_objs.append(User.query.get(friend_id))
    # Lấy danh sách request pending (gửi đến mình)
    pending = Friend.query.filter_by(user_id_2=uid, status="pending").all()
    pending_senders = [User.query.get(r.user_id_1) for r in pending]

    # Bạn có thể hiện thêm danh sách tất cả user (để gửi kết bạn)
    all_users = User.query.filter(User.user_id != uid).all()
    return render_template(
        "friends.html",
        friends=friends_objs,
        requests=pending_senders,
        all_users=all_users
    )

@friends_bp.route("/send/<int:to_id>", methods=["POST"])
@login_required
def send_request(to_id):
    uid = session["user_id"]
    # Kiểm tra đã có record nào chưa
    exists = Friend.query.filter(
        ((Friend.user_id_1 == uid) & (Friend.user_id_2 == to_id)) |
        ((Friend.user_id_1 == to_id) & (Friend.user_id_2 == uid))
    ).first()
    if exists:
        flash("Đã gửi request hoặc hai bạn đã là bạn.", "warning")
        return redirect(url_for("friends.friends_list"))

    new_req = Friend(user_id_1=uid, user_id_2=to_id, status="pending")
    db.session.add(new_req)
    db.session.commit()
    flash("Đã gửi lời mời kết bạn.", "success")
    return redirect(url_for("friends.friends_list"))

@friends_bp.route("/accept/<int:from_id>", methods=["POST"])
@login_required
def accept_request(from_id):
    uid = session["user_id"]
    req = Friend.query.filter_by(user_id_1=from_id, user_id_2=uid, status="pending").first()
    if req:
        req.status = "accepted"
        db.session.commit()
        flash("Đã chấp nhận kết bạn.", "success")
    return redirect(url_for("friends.friends_list"))

@friends_bp.route("/remove/<int:friend_id>", methods=["POST"])
@login_required
def remove_friend(friend_id):
    uid = session["user_id"]
    rel = Friend.query.filter(
        ((Friend.user_id_1 == uid) & (Friend.user_id_2 == friend_id)) |
        ((Friend.user_id_1 == friend_id) & (Friend.user_id_2 == uid))
    ).first()
    if rel:
        db.session.delete(rel)
        db.session.commit()
        flash("Đã xóa bạn.", "info")
    return redirect(url_for("friends.friends_list"))
