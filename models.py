from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import backref
from datetime import datetime

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
    travel_budget = db.Column(db.Integer, nullable=False)      # 预算，改为整数类型
    max_members = db.Column(db.Integer, nullable=False)
    current_members = db.Column(db.Integer, nullable=False)
    public_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    travel_plan = db.Column(db.Text)  # 新增旅游计划景点字段
    popularity = db.Column(db.Integer, default=0, nullable=False)  # 新增队伍热度统计字段
    view_count = db.Column(db.Integer, default=0, nullable=False)  # 新增查看次数字段
    apply_count = db.Column(db.Integer, default=0, nullable=False)  # 新增入队申请次数字段
    team_admin = db.relationship('User', foreign_keys=[admin_id])

    # 实时计算队伍热度
    def update_popularity(self):
        self.popularity = 0.5 * self.view_count + 1.0 * self.apply_count + 1.5 * self.current_members
        db.session.commit()
    # # 定义了两个关系属性 admin 和 public, 其分别表示了队伍的管理员和创建者。
    # admin = db.relationship('User', foreign_keys=[admin_id], backref=db.backref('owned_teams', lazy=True))
    # public = db.relationship('User', foreign_keys=[public_id], backref=db.backref('created_teams', lazy=True))


# 存储邀请信息
class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    inviter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 状态：pending, accepted, declined

    team = db.relationship('Team', backref=db.backref('invitations', lazy='dynamic'))
    inviter = db.relationship('User', foreign_keys=[inviter_id])
    invitee = db.relationship('User', foreign_keys=[invitee_id])


# 存储景点信息
class Attractions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    城市 = db.Column(db.String(50))
    景点名称 = db.Column(db.String(100))
    攻略数量 = db.Column(db.String(50))
    评论数量 = db.Column(db.String(50))
    星级 = db.Column(db.Float)
    排名 = db.Column(db.String(50))
    简介 = db.Column(db.Text)
    链接 = db.Column(db.String(255))
    图片 = db.Column(db.String(255))


# 存储通知消息
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(200), nullable=True)

    user = db.relationship('User', backref='notifications')
