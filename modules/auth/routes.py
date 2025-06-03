# modules/auth/routes.py
from flask import render_template, request, redirect, url_for, session, flash
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, mail
from models import User
from random import randint
from . import auth_bp
from flask import current_app


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        email = request.form.get("email").strip()
        password = request.form.get("password").strip()
        # Kiểm tra trống, kiểm tra tồn tại username/email
        if not username or not email or not password:
            flash("Vui lòng điền đủ thông tin.", "danger")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        if existing_user:
            flash("Username hoặc email đã tồn tại.", "danger")
            return redirect(url_for("auth.register"))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Đăng ký thành công. Hãy đăng nhập!", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.user_id
            session["username"] = user.username
            return redirect(url_for("posts.feed"))
        flash("Thông tin đăng nhập không đúng.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")

# Step 1: Nhập username để gửi OTP
@auth_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        username = request.form.get("username").strip()
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Không tìm thấy tài khoản với username này.", "danger")
            return redirect(url_for("auth.forgot_password"))

        # Tạo OTP 4 chữ số ngẫu nhiên
        otp = randint(1000, 9999)
        session["reset_otp"] = str(otp)
        session["reset_user_id"] = user.user_id

        # Gửi mail OTP (thêm try-except để bắt lỗi)
        try:
            msg = Message(
                subject="OTP lấy lại mật khẩu",
                sender=("Social Network App", "trananhviet18nd@gmail.com"),
                recipients=[user.email]
            )
            msg.body = f"""Chào {user.username},

Bạn vừa yêu cầu lấy lại mật khẩu.

Mã OTP của bạn là: {otp}

Vui lòng không chia sẻ mã này với bất kỳ ai. Mã sẽ hết hạn sau vài phút.

Trân trọng,
Hỗ trợ Social Network Web
"""
            mail.send(msg)
            flash("Mã OTP đã được gửi đến email của bạn.", "info")
            return redirect(url_for("auth.reset_password"))

        except Exception as e:
            print(f"❌ Gửi email thất bại: {str(e)}") 
            flash("Không thể gửi email. Vui lòng thử lại sau.", "danger")
            return redirect(url_for("auth.forgot_password"))
        
    print("MAIL_USERNAME trong route:", current_app.config.get("MAIL_USERNAME"))
    print("MAIL_PASSWORD trong route:", current_app.config.get("MAIL_PASSWORD"))

    
    return render_template("forgot_password.html")


# Step 2: Nhập OTP và mật khẩu mới
@auth_bp.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        otp_input = request.form.get("otp").strip()
        new_password = request.form.get("new_password").strip()
        confirm_password = request.form.get("confirm_password").strip()

        if otp_input != session.get("reset_otp"):
            flash("Mã OTP không đúng.", "danger")
            return redirect(url_for("auth.reset_password"))

        if new_password != confirm_password or not new_password:
            flash("Mật khẩu mới không khớp hoặc trống.", "danger")
            return redirect(url_for("auth.reset_password"))

        user_id = session.get("reset_user_id")
        if not user_id:
            flash("Phiên làm việc hết hạn, vui lòng thử lại.", "danger")
            return redirect(url_for("auth.forgot_password"))

        user = User.query.get(user_id)
        if not user:
            flash("Không tìm thấy người dùng.", "danger")
            return redirect(url_for("auth.forgot_password"))

        from werkzeug.security import generate_password_hash
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Xóa session OTP và user_id
        session.pop("reset_otp", None)
        session.pop("reset_user_id", None)

        flash("Đổi mật khẩu thành công. Hãy đăng nhập lại.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
