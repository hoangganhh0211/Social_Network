# modules/profile/routes.py
import os
from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import User, Post
from extensions import db
from flask import abort


from flask import Blueprint
profile_bp = Blueprint("profile", __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route("/<int:user_id>")
def view_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    return render_template("profile/view.html", user=user, posts=posts)

@profile_bp.route("/upload_avatar", methods=["POST"])
def upload_avatar():
    if "user_id" not in session:
        flash("Bạn cần đăng nhập trước.")
        return redirect(url_for("auth.login"))
    
    file = request.files.get("avatar")
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        user_id = session["user_id"]
        upload_folder = os.path.join(current_app.root_path, "static", "avatars")
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, f"user_{user_id}_{filename}")
        file.save(file_path)

        # Cập nhật đường dẫn ảnh đại diện vào DB
        user = User.query.get(user_id)
        user.avatar_url = f"/static/avatars/user_{user_id}_{filename}"
        db.session.commit()

        flash("Cập nhật ảnh đại diện thành công.")
    else:
        flash("Tập tin không hợp lệ.")
    
    return redirect(url_for("profile.view_profile", user_id=session["user_id"]))

# Mới: Xoá bài đăng của chính người dùng
@profile_bp.route("/delete_post/<int:post_id>", methods=["POST"])
def delete_post(post_id):
    if "user_id" not in session:
        flash("Bạn cần đăng nhập trước.")
        return redirect(url_for("auth.login"))

    post = Post.query.get_or_404(post_id)
    # Chỉ cho phép xóa bài của chính chủ
    if post.user_id != session["user_id"]:
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash("Đã xoá bài viết thành công.")
    return redirect(url_for("profile.view_profile", user_id=session["user_id"]))