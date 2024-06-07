from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import backref

db = SQLAlchemy()

# 中间表，用于存储用户和队伍的关系
team_membership = db.Table('user_team',
                           db.Column('join_user_id', db.Integer, db.ForeignKey(
                               'user.id'), primary_key=True),
                           db.Column('team_id', db.Integer, db.ForeignKey(
                               'team.id'), primary_key=True),
                           # 0: pending, 1: approved, 2: denied
                           db.Column('audit_status', db.Integer,
                                     default=0, nullable=False)
                           )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20))
    teams = db.relationship('Team', secondary=team_membership,
                            backref=db.backref('members', lazy='dynamic'))


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination = db.Column(db.String(150), nullable=False, comment='目的地')
    departure_location = db.Column(
        db.String(150), nullable=False, comment='出发地点')
    travel_mode = db.Column(db.String(150), nullable=False, comment='出行方式')
    team_type = db.Column(db.String(150), nullable=False, comment='队伍类型')
    travel_time = db.Column(db.String(150), nullable=False, comment='游玩时间')
    travel_budget = db.Column(db.String(150), nullable=False, comment='旅游预算')
    max_members = db.Column(db.Integer, nullable=True,
                            default=0, comment='组队人数')
    current_members = db.Column(
        db.Integer, nullable=False, default=0, comment='当前组队人数')
    public_id = db.Column(db.Integer, nullable=False,
                          comment='发起人id（关联user表的id）')
    admin_id = db.Column(db.Integer, nullable=True,
                         default=1, comment='管理员id（关联user表的id）')


# class UserTeam(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
#     join_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
#     audit_status = db.Column(db.Integer, default=0, nullable=False)
#
#     user = db.relationship('User', backref='user_teams')
#     team = db.relationship('Team', backref='user_teams')
