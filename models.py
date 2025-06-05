from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, BOOLEAN, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from extensions import db
from flask_login import UserMixin

# Bảng Lưu thông tin người dùng
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    avatar_url = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Quan hệ đến Post: 1 User có thể có nhiều Post
    posts = relationship('Post', back_populates='user', cascade='all, delete-orphan') 
    
    # Quan hệ tới notifications
    notifications = relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    

    # Override get_id() để Flask-Login dùng user_id: do flask login cần để xác định id
    def get_id(self):
        return str(self.user_id)
    
# Bảng Lưu bài viết.
class Post(db.Model):
    __tablename__ = 'posts'
    post_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(Text, nullable=False)
    media_url = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Quan hệ hai chiều với User
    user = relationship('User', back_populates='posts')
    # Quan hệ hai chiều với Comment
    comments = relationship('Comment', back_populates='post', cascade='all, delete-orphan')

# Bảng Lưu bình luận.
class Comment(db.Model):
    __tablename__ = 'comments'
    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.post_id'))
    user_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    post = relationship('Post', back_populates='comments')
    user = relationship('User')
    
# Bảng Lưu hashtag
class Hashtag(db.Model):
    __tablename__ = 'hashtags'
    hashtag_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)

# Bảng Liên kết giữa bài viết và hashtag.
class PostHashtag(db.Model):
    __tablename__ = 'post_hashtags'
    post_id = Column(Integer, ForeignKey('posts.post_id'), primary_key=True)
    hashtag_id = Column(Integer, ForeignKey('hashtags.hashtag_id'), primary_key=True)

# Bảng Quản lý quan hệ bạn bè.
class Friend(db.Model):
    __tablename__ = 'friends'
    friendship_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id_1 = Column(Integer, ForeignKey('users.user_id'))
    user_id_2 = Column(Integer, ForeignKey('users.user_id'))
    status = Column(String(20))
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

# Bảng Lưu tin nhắn.
class Message(db.Model):
    __tablename__ = 'messages'
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.user_id'))
    receiver_id = Column(Integer, ForeignKey('users.user_id'))
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    is_read = Column(BOOLEAN, default=False)
    
class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)   # người nhận thông báo
    # Loại thông báo
    notif_type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    reference_id = Column(Integer, nullable=True)
    is_read = Column(BOOLEAN, default=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    # Quan hệ với User để dễ join
    user = relationship('User', back_populates='notifications')