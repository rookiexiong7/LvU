from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(150), nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    current_members = db.Column(db.Integer, default=0)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin = db.relationship('User', backref=db.backref('teams', lazy=True))
