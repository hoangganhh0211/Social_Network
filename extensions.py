# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail
from flask_socketio import SocketIO
from flask_login import LoginManager

db = SQLAlchemy()
sess = Session()
mail = Mail()
socketio = SocketIO()
login_manager = LoginManager()