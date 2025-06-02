# modules/auth/__init__.py
from flask import Blueprint

auth_bp = Blueprint(
    "auth", 
    __name__, 
    template_folder="../../templates/auth"  # để Flask tìm đúng thư mục templates/auth
)
