# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail

db = SQLAlchemy()
sess = Session()
mail = Mail()