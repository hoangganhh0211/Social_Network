import os
from flask import Flask
from extensions import db, sess, mail
from modules.auth.routes import auth_bp
from modules.posts.routes import posts_bp
from modules.friends.routes import friends_bp
from modules.messages.routes import messages_bp
from config import Config  # import cấu hình


app = Flask(__name__)
app.config.from_object(Config)  # load config từ class Config

# Khởi tạo extensions
db.init_app(app)
sess.init_app(app)
mail.init_app(app)

# Đăng ký các blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(posts_bp, url_prefix="/posts")
app.register_blueprint(friends_bp, url_prefix="/friends")
app.register_blueprint(messages_bp, url_prefix="/messages")

@app.route("/")
def index():
    from flask import session, redirect, url_for
    if session.get("user_id"):
        return redirect(url_for("posts.feed"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
