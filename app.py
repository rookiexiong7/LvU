from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, TeamForm
from forms import ManageTeamForm  # 新增管理队伍的表单
from models import db, User, Team, team_membership

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
# 配置 MySQL 数据库连接 密码为本地root用户密码
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/lvu'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    #     user = User(username=form.username.data, password=hashed_password)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('Your account has been created!', 'success')
    #     return redirect(url_for('login'))
    # return render_template('register.html', form=form)
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


# 用户登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user and bcrypt.check_password_hash(user.password, form.password.data):
    #         login_user(user, remember=True)
    #         return redirect(url_for('home'))
    #     else:
    #         flash('Login Unsuccessful. Please check username and password', 'danger')
    # return render_template('login.html', form=form)
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)


# 创建队伍
@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamForm()
    user = current_user
    if form.validate_on_submit():
        print(f"Creating team with public_id and admin_id set to: {user.id}")  # 调试信息
        team = Team(
            destination=form.destination.data,
            max_members=form.max_members.data,
            current_members=0,
            public_id=user.id,     # 使用 user 对象作为 public
            admin_id=user.id       # 使用 user 对象作为 admin
        )
        db.session.add(team)

        # 将队伍创建者加入到队伍中
        user.teams.append(team)
        team.current_members += 1

        # 更新user_team表中的audit_status字段
        db.session.execute(
            'INSERT INTO user_team (team_id, join_user_id, audit_status) VALUES (:team_id, :user_id, :audit_status)',
            {'team_id': team.id, 'user_id': user.id, 'audit_status': 1}
        )

        db.session.commit()
        flash('Your team has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_team.html', form=form)


# 加入队伍
@app.route('/join_team/<int:team_id>', methods=['POST'])
@login_required
def join_team(team_id):
    # team = Team.query.get_or_404(team_id)
    # user = current_user
    #
    # if team in user.teams:
    #     flash('You have already joined this team.')
    #     return redirect(url_for('home'))
    #
    # if team.current_members >= team.max_members:
    #     flash('This team is full.')
    #     return redirect(url_for('home'))
    #
    # team.current_members += 1
    # user.teams.append(team)
    # db.session.commit()
    #
    # flash('You have successfully joined the team.')
    # return redirect(url_for('home'))
    team = Team.query.get_or_404(team_id)
    user = current_user

    if team.current_members >= team.max_members:
        flash('This team is full.')
        return redirect(url_for('home'))

    if team in user.teams:
        flash('You have already requested to join this team.')
        return redirect(url_for('home'))

    # 插入新的申请记录，设置 audit_status 为 0
    ins = team_membership.insert().values(join_user_id=user.id, team_id=team.id, audit_status=0)
    db.session.execute(ins)
    db.session.commit()

    flash('Join request sent to the team admin.')
    return redirect(url_for('home'))


# 同意加入队伍申请
@app.route('/approve_request/<int:join_user_id>/<int:team_id>', methods=['POST'])
@login_required
def approve_request(join_user_id, team_id):
    team = Team.query.get_or_404(team_id)

    if team.admin_id != current_user.id:
        flash('You do not have permission to approve this request.')
        return redirect(url_for('home'))

    # 更新申请状态为1（审核通过）
    stmt = team_membership.update().where(
        team_membership.c.join_user_id == join_user_id,
        team_membership.c.team_id == team_id
    ).values(audit_status=1)
    db.session.execute(stmt)
    team.current_members += 1
    db.session.commit()

    flash('Request approved.')
    return redirect(url_for('team_requests'))


# 拒绝加入队伍申请
@app.route('/deny_request/<int:join_user_id>/<int:team_id>', methods=['POST'])
@login_required
def deny_request(join_user_id, team_id):
    team = Team.query.get_or_404(team_id)
    if team.admin_id != current_user.id:
        flash('You do not have permission to deny this request.')
        return redirect(url_for('home'))

    # 更新申请状态为2（审核不通过）
    stmt = team_membership.update().where(
        team_membership.c.join_user_id == join_user_id,
        team_membership.c.team_id == team_id
    ).values(audit_status=2)
    db.session.execute(stmt)
    db.session.commit()

    flash('Request denied.')
    return redirect(url_for('team_requests'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    teams = Team.query.filter_by(admin_id=current_user.id).all()
    return render_template('admin_dashboard.html', teams=teams)


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
        request_id = f"{request_info.join_user_id}-{request_info.team_id}"  # 用用户ID和队伍ID作为唯一标识符
        requests_dict[request_id] = {
            'username': request_info.username,
            'destination': request_info.destination,
            'join_user_id': request_info.join_user_id,
            'team_id': request_info.team_id
        }

    print(requests_dict)

    return render_template('team_requests.html', requests_dict=requests_dict)


# 用户登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@app.route('/home')
def home():
    teams = Team.query.all()
    return render_template('home.html', teams=teams)


# 队伍成员查看队伍信息
@app.route('/team/<int:team_id>', methods=['GET'])
@login_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    approved_members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team_id,
        team_membership.c.audit_status == 1
    ).all()
    return render_template('view_team.html', team=team, approved_members=approved_members)


# 管理员更改队伍信息
@app.route('/manage_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def manage_team(team_id):
    team = Team.query.get_or_404(team_id)
    if team.admin_id != current_user.id:
        flash('You do not have permission to manage this team.')
        return redirect(url_for('home'))

    form = ManageTeamForm(obj=team)

    if form.validate_on_submit():
        team.destination = form.destination.data
        team.max_members = form.max_members.data
        db.session.commit()
        flash('Team information updated successfully!', 'success')
        return redirect(url_for('manage_team', team_id=team.id))

    members = team.members
    return render_template('manage_team.html', team=team, form=form, members=members)


# 管理员移除队员
@app.route('/remove_member/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
def remove_member(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    user = User.query.get_or_404(user_id)

    # 检查当前用户是否是队伍管理员
    if team.admin_id != current_user.id:
        flash('You do not have permission to remove members from this team.')
        return redirect(url_for('manage_team', team_id=team_id))

    # 检查要删除的用户是否是队伍管理员本人
    if user.id == current_user.id:
        flash('You cannot remove yourself from the team as an admin.')
        return redirect(url_for('manage_team', team_id=team_id))

    if user in team.members:
        team.members.remove(user)
        team.current_members -= 1
        db.session.commit()
        flash('Member removed successfully!', 'success')
    return redirect(url_for('manage_team', team_id=team_id))


if __name__ == '__main__':
    app.run(debug=True)
