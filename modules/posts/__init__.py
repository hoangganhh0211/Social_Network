from flask import Blueprint
from .games.routes import games_bp  # nếu bạn có games_bp
from .routes import posts_bp  # import blueprint chính từ routes.py

def register_posts_blueprints(app):
    app.register_blueprint(posts_bp)     # blueprint chính
    app.register_blueprint(games_bp)     # sub-blueprint games
