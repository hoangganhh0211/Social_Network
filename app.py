from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from models import *
from datetime import date


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456789@Localhost:5432/Social_Network'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

