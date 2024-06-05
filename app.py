from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import text

from forms import RegistrationForm, LoginForm, TeamForm
from forms import ManageTeamForm  # 新增管理队伍的表单
from models import db, User, Team, team_membership

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# 配置 MySQL 数据库连接 密码为本地root用户密码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/lvu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/index', methods=['GET', 'POST'])
def index():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []
    username = current_user.username

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('index.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams, username=username)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    print(form.password.data, form.confirm_password.data)
    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            username=form.username.data).first()
        if existing_user is None:
            user = User(username=form.username.data,
                        password=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('注册成功', 'success')
        else:
            flash('用户名已存在', 'danger')
    if form.password.data is not None and form.confirm_password.data is not None and form.password.data != form.confirm_password.data:
        flash('两次密码不一致', 'danger')
    return render_template('page/register.html', form=form)


# 用户登录
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=True)
            flash('登录成功！', 'success')
        else:
            flash('登录失败，请检查账号密码是否正确！', 'danger')
    return render_template('page/login.html', form=form)


# 创建队伍
@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamForm()
    user = current_user
    if form.validate_on_submit():
        # 调试信息
        print(f"Creating team with public_id and admin_id set to: {user.id}")
        team = Team(
            destination=form.destination.data,
            max_members=form.max_members.data,
            current_members=1,  # 创建时包含队伍创建者
            public_id=user.id,  # 记录队伍创建者
            admin_id=user.id  # 初始化管理员为队伍创建者
        )
        db.session.add(team)
        db.session.flush()  # 刷新 session 以获取新创建的 team.id

        # 将队伍创建者加入到队伍中, 并设置 audit_status 为 1
        db.session.execute(
            text(
                'INSERT INTO user_team (team_id, join_user_id, audit_status) VALUES (:team_id, :user_id, :audit_status)'),
            {'team_id': team.id, 'user_id': user.id, 'audit_status': 1}
        )

        db.session.commit()
        flash('您的队伍已创建！', 'success')
        return redirect(url_for('my_manage_team'))
    return render_template('page/create_team.html', form=form)


@app.route('/sending_requests', methods=['GET', 'POST'])
def sending_requests():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []
    username = current_user.username

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('page/sending_requests.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams, username=username)

# 加入队伍


@app.route('/join_team/<int:team_id>', methods=['POST'])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)
    user = current_user

    if team.current_members >= team.max_members:
        flash('T该队伍已满员。')
        return redirect(url_for('joinable_teams'))

    if team in user.teams:
        flash('您已申请加入该队伍。')
        return redirect(url_for('joinable_teams'))

    # 插入新的申请记录，设置 audit_status 为 0
    ins = team_membership.insert().values(
        join_user_id=user.id, team_id=team.id, audit_status=0)
    db.session.execute(ins)
    db.session.commit()

    flash('加入请求已成功发送给队伍管理员。', 'success')
    return redirect(url_for('joinable_teams'))


# 同意加入队伍申请
@app.route('/approve_request/<int:join_user_id>/<int:team_id>', methods=['POST'])
@login_required
def approve_request(join_user_id, team_id):
    team = Team.query.get_or_404(team_id)

    if team.admin_id != current_user.id:
        flash('您没有权限批准此请求。')
        return redirect(url_for('team_requests'))

    # 更新申请状态为1（审核通过）
    stmt = team_membership.update().where(
        team_membership.c.join_user_id == join_user_id,
        team_membership.c.team_id == team_id
    ).values(audit_status=1)
    db.session.execute(stmt)
    team.current_members += 1
    db.session.commit()

    flash('请求已通过！', 'success')
    return redirect(url_for('team_requests'))


# 拒绝加入队伍申请
@app.route('/deny_request/<int:join_user_id>/<int:team_id>', methods=['POST'])
@login_required
def deny_request(join_user_id, team_id):
    team = Team.query.get_or_404(team_id)
    if team.admin_id != current_user.id:
        flash('您没有权限拒绝此请求。')
        return redirect(url_for('team_requests'))

    # 更新申请状态为2（审核不通过）
    stmt = team_membership.update().where(
        team_membership.c.join_user_id == join_user_id,
        team_membership.c.team_id == team_id
    ).values(audit_status=2)
    db.session.execute(stmt)
    db.session.commit()

    flash('请求已成功拒绝！', 'success')
    return redirect(url_for('team_requests'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    teams = Team.query.filter_by(admin_id=current_user.id).all()
    return render_template('page/admin_dashboard.html', teams=teams)


# 管理员待处理申请
@app.route('/team_requests', methods=['GET'])
@login_required
def team_requests():
    # 获取当前用户管理的所有队伍
    teams = Team.query.filter_by(admin_id=current_user.id).all()
    team_ids = [team.id for team in teams]

    # 查询待处理的申请
    pending_requests = db.session.query(User.username, Team.destination, team_membership.c.join_user_id,
                                        team_membership.c.team_id) \
        .join(User, User.id == team_membership.c.join_user_id) \
        .join(Team, Team.id == team_membership.c.team_id) \
        .filter(team_membership.c.team_id.in_(team_ids), team_membership.c.audit_status == 0).all()

    # 将查询结果包装成字典形式
    requests_dict = {}
    for request_info in pending_requests:
        # 用用户ID和队伍ID作为唯一标识符
        request_id = f"{request_info.join_user_id}-{request_info.team_id}"
        requests_dict[request_id] = {
            'username': request_info.username,
            'destination': request_info.destination,
            'join_user_id': request_info.join_user_id,
            'team_id': request_info.team_id
        }

    print(requests_dict)

    return render_template('page/team_requests.html', requests_dict=requests_dict)


# 用户登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/user_setting', methods=['GET', 'POST'])
def user_setting():
    return render_template('page/user_setting.html')


@app.route('/user_password', methods=['GET', 'POST'])
def user_password():
    return render_template('page/user_password.html')


@app.route('/home')
def home():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []
    username = current_user.username

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('page/home.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams, username=username)


# 队伍成员查看队伍信息
@app.route('/team/<int:team_id>', methods=['GET'])
@login_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    approved_members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team_id,
        team_membership.c.audit_status == 1
    ).all()
    return render_template('page/view_team.html', team=team, approved_members=approved_members)


@app.route('/my_manage_team', methods=['GET'])
@login_required
def my_manage_team():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
    return render_template('page/my_manage_team.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams)


@app.route('/my_join_team', methods=['GET'])
@login_required
def my_join_team():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1 and team.admin_id != current_user.id:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
    return render_template('page/my_join_team.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams)


@app.route('/joinable_teams', methods=['GET'])
@login_required
def joinable_teams():
    teams = Team.query.all()
    current_user_teams = current_user.teams
    approved_teams = []
    pending_teams = []
    username = current_user.username

    for team in current_user_teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()
        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('page/joinable_teams.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams, username=username)


# 管理员更改队伍信息
@app.route('/manage_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def manage_team(team_id):
    team = Team.query.get_or_404(team_id)

    if team.admin_id != current_user.id:
        flash('您没有权限管理此队伍。', 'danger')
        return redirect(url_for('my_manage_team'))

    form = ManageTeamForm(obj=team)

    if form.validate_on_submit():
        if form.max_members.data < team.current_members:  # 判断设置的最大人数是否小于当前队伍中的人数
            flash(
                f'无法将队伍的最大人数设置为{form.max_members.data}，因为它小于当前的队伍人数 {team.current_members}.',
                'danger')
        else:
            team.destination = form.destination.data
            team.max_members = form.max_members.data
            db.session.commit()
            flash('成功更新队伍信息！', 'success')

        return redirect(url_for('manage_team', team_id=team.id))

    # 只获取审核通过的成员
    members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team.id,
        team_membership.c.audit_status == 1
    ).all()

    return render_template('manage_team.html', team=team, form=form, members=members)


# 管理员移除队员
@app.route('/remove_member/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    user = User.query.get_or_404(user_id)

    # 检查当前用户是否是队伍管理员
    if team.admin_id != current_user.id:
        flash('您目前没有权限从该队伍中移除成员。')
        return redirect(url_for('manage_team', team_id=team_id))

    # 检查要删除的用户是否是队伍管理员本人
    if user.id == current_user.id:
        flash('您作为管理员不能将自己从队伍中移除。')
        return redirect(url_for('manage_team', team_id=team_id))

    if user in team.members:
        team.members.remove(user)
        team.current_members -= 1
        db.session.commit()
        flash('成员已成功移除！', 'success')

    return redirect(url_for('manage_team', team_id=team_id))


# 管理员移交管理员权限
@app.route('/transfer_admin/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
def transfer_admin(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    if team.admin_id != current_user.id:
        flash(
            '您没有权限转移此队伍的管理员权限。', 'danger')
        return redirect(url_for('manage_team', team_id=team.id))

    new_admin = User.query.get_or_404(user_id)
    if new_admin not in team.members:
        flash('此用户不是该队伍的成员。', 'danger')
        return redirect(url_for('manage_team', team_id=team.id))

    team.admin_id = new_admin.id
    db.session.commit()

    flash(f'管理员权限已转移给 {new_admin.username}.', 'success')
    return redirect(url_for('manage_team', team_id=team.id))


if __name__ == '__main__':
    app.run(debug=True)
