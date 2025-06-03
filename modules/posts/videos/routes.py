# modules/posts/videos/routes.py
from flask import Blueprint, render_template

videos_bp = Blueprint('videos', __name__, url_prefix='/templates/videos', template_folder='templates')

@videos_bp.route("/")
def video_index():
    return render_template("videos/index.html")