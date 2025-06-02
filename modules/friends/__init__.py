# modules/friends/__init__.py
from flask import Blueprint

friends_bp = Blueprint(
    "friends",
    __name__,
    template_folder="../../templates/friends"
)
