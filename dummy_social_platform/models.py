from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'dp_users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(512))
    bio = db.Column(db.String(140))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    likes = db.relationship('Like', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Post(db.Model):
    __tablename__ = 'dp_posts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('dp_users.id'), nullable=False)
    image_filename = db.Column(db.String(120), nullable=True)
    caption = db.Column(db.String(280))
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_taken_down = db.Column(db.Boolean, default=False)
    taken_down_at = db.Column(db.DateTime)
    taken_down_reason = db.Column(db.String(280))
    taken_down_case_id = db.Column(db.String(64))
    likes = db.relationship('Like', backref='post', lazy='dynamic')

class Like(db.Model):
    __tablename__ = 'dp_likes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('dp_users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('dp_posts.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
