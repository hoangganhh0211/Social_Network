from flask import Blueprint, render_template
from flask_login import login_required, current_user
from modules.auth.routes import User

games_bp = Blueprint('games', __name__, url_prefix='/games')

# Trang danh sách các trò chơi
@games_bp.route('/')
def games_home():
    return render_template('posts/games/game_list.html')

# Trò chơi 1: Bắt bóng
@games_bp.route('/game1')
def game1():
    # Truy vấn tất cả bạn bè (hoặc tất cả users trừ chính user)
    friends = User.query.filter(User.user_id != current_user.user_id).all()
    return render_template('posts/games/game_play_1.html', friends=friends)

# Trò chơi 2: ví dụ đơn giản khác
@games_bp.route('/game2')
def game2():
    return render_template('posts/games/game_play_2.html')
