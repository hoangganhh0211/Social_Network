import os
from flask import Flask
from flask_migrate import Migrate
from extensions import db, sess, mail
from modules.auth.routes import auth_bp
from modules.posts.routes import posts_bp
from modules.friends.routes import friends_bp
from modules.messages.routes import messages_bp
from modules.profile.routes import profile_bp
from config import Config  # import cấu hình
from extensions import socketio

from modules.posts.routes import register_posts_blueprints

app = Flask(__name__)
migrate = Migrate()
app.config.from_object(Config)  # load config từ class Config

# Khởi tạo extensions
db.init_app(app)
sess.init_app(app)
mail.init_app(app)
socketio.init_app(app)

migrate.init_app(app, db)

# Gọi xử lý yêu cầu 
from modules.messages.routes import register_events
register_events(socketio)

# Đăng ký các blueprint
app.register_blueprint(auth_bp, url_prefix="/auth")
register_posts_blueprints(app)
app.register_blueprint(friends_bp, url_prefix="/friends")
app.register_blueprint(messages_bp, url_prefix="/messages")
app.register_blueprint(profile_bp, url_prefix="/profile")

@app.route("/")
def index():
    from flask import session, redirect, url_for
    if session.get("user_id"):
        return redirect(url_for("posts.feed"))
    return redirect(url_for("auth.login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # Dùng socketio.run thay vì app.run để hỗ trợ websocket
    socketio.run(app, debug=True)
