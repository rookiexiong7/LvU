from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import backref

db = SQLAlchemy()

# 中间表，用于存储用户和队伍的关系
team_membership = db.Table('user_team',
                           db.Column('join_user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                           db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
                           db.Column('audit_status', db.Integer, default=0, nullable=False)  # 0: pending, 1: approved, 2: denied
                           )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    teams = db.relationship('Team', secondary=team_membership, backref=db.backref('members', lazy='dynamic'))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(150), nullable=False)
    max_members = db.Column(db.Integer, nullable=False)
    current_members = db.Column(db.Integer, default=0, nullable=False)
    public_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # # 定义了两个关系属性 admin 和 public, 其分别表示了队伍的管理员和创建者。
    # # 这样当设置 public_id 和 admin_id 为用户对象时，SQLAlchemy 会自动处理关系的关联, 防止报错
    # admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('owned_teams', lazy=True))
    # public = db.relationship('User', foreign_keys=[public_id], backref=db.backref('created_teams', lazy=True))


# class UserTeam(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
#     join_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     audit_status = db.Column(db.Integer, default=0, nullable=False)
#
#     user = db.relationship('User', backref='user_teams')
#     team = db.relationship('Team', backref='user_teams')
