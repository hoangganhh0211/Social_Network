# modules/posts/routes.py
from flask import (
    render_template, request, redirect, url_for, session, flash
)
from extensions import db
from models import Post, Comment, Hashtag, PostHashtag, User
from . import posts_bp

# Yêu cầu user đã đăng nhập mới vào được feed
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return fn(*args, **kwargs)
    return wrapper

@posts_bp.route("/feed")
@login_required
def feed():
    # Lấy tất cả bài post, sắp theo thời gian giảm dần
    all_posts = Post.query.order_by(Post.created_at.desc()).all()

    # Đổi post thành list dict chứa user + comment count để template dễ hiển thị
    posts_data = []
    for p in all_posts:
        usr = User.query.get(p.user_id)
        comment_count = Comment.query.filter_by(post_id=p.post_id).count()
        posts_data.append({
            "post": p,
            "user": usr,
            "comment_count": comment_count
        })
    return render_template("feed.html", posts=posts_data)


@posts_bp.route("/create", methods=["POST"])
@login_required
def create_post():
    content = request.form.get("content").strip()
    media_url = request.form.get("media_url").strip() or None
    if not content:
        flash("Nội dung bài viết không được để trống.", "danger")
        return redirect(url_for("posts.feed"))

    new_post = Post(
        user_id=session["user_id"],
        content=content,
        media_url=media_url
    )
    db.session.add(new_post)
    db.session.commit()

    # Xử lý hashtag (nếu người dùng gõ #têntag trong content)
    words = content.split()
    for w in words:
        if w.startswith("#") and len(w) > 1:
            tag_name = w[1:].lower()
            hashtag = Hashtag.query.filter_by(name=tag_name).first()
            if not hashtag:
                hashtag = Hashtag(name=tag_name)
                db.session.add(hashtag)
                db.session.flush()  # để có id trước khi commit
            # Tạo liên kết PostHashtag
            ph = PostHashtag(post_id=new_post.post_id, hashtag_id=hashtag.hashtag_id)
            db.session.add(ph)
    db.session.commit()

    return redirect(url_for("posts.feed"))


@posts_bp.route("/<int:post_id>", methods=["GET", "POST"])
@login_required
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    author = User.query.get(post.user_id)
    # Lấy tất cả bình luận kèm user
    comments = (
        db.session.query(Comment, User.username)
        .join(User, Comment.user_id == User.user_id)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )

    # Nếu submit comment
    if request.method == "POST":
        content = request.form.get("content").strip()
        if content:
            new_cmt = Comment(
                post_id=post_id,
                user_id=session["user_id"],
                content=content
            )
            db.session.add(new_cmt)
            db.session.commit()
            return redirect(url_for("posts.post_detail", post_id=post_id))

    return render_template(
        "post_detail.html",
        post=post,
        author=author,
        comments=comments
    )
