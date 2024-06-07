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
    id_code = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    character = db.Column(db.String(100))
    travel_hobby = db.Column(db.String(150))
    residence = db.Column(db.String(150))   # 居住地
    gender = db.Column(db.String(10))
    teams = db.relationship('Team', secondary=team_membership, backref=db.backref('members', lazy='dynamic'))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(150), nullable=False)
    departure_location = db.Column(db.String(150), nullable=False)
    travel_mode = db.Column(db.String(100))                    # 出行方式
    team_type = db.Column(db.String(100))                      # 队伍类型
    travel_time = db.Column(db.String(100), nullable=False)    # 出行时间
    travel_budget = db.Column(db.String(100), nullable=False)  # 预算
    max_members = db.Column(db.Integer, nullable=False)
    current_members = db.Column(db.Integer, nullable=False)
    public_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # # 定义了两个关系属性 admin 和 public, 其分别表示了队伍的管理员和创建者。
    # admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('owned_teams', lazy=True))
    # public = db.relationship('User', foreign_keys=[public_id], backref=db.backref('created_teams', lazy=True))
