from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(255))
    email = db.Column(db.String(120), unique=True, nullable=False)
    user_type = db.Column(db.String(20), default='disabled')  # 'disabled' or 'volunteer'
    skills = db.Column(db.String(200))  # 逗号分隔的技能字符串
    rating = db.Column(db.Float, default=5.0)
    is_online = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 关系
    help_requests = db.relationship('HelpRequest', backref='author', lazy=True)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.username}>'


class HelpRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # 'visual', 'hearing', 'other'
    status = db.Column(db.String(20), default='pending')  # pending/accepted/completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    def __repr__(self):
        return f'<HelpRequest {self.title}>'


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    help_request_id = db.Column(db.Integer, db.ForeignKey('help_request.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id])
    receiver = db.relationship('User', foreign_keys=[receiver_id])
    help_request = db.relationship('HelpRequest')