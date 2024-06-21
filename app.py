import json

import pymysql
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import text, and_, func, Integer, cast

from forms import RegistrationForm, LoginForm, TeamForm, UserForm
from forms import ManageTeamForm  # 新增管理队伍的表单
from models import db, User, Team, team_membership, Invitation, Attractions, Notification

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

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('index.html', teams=teams, approved_teams=approved_teams, pending_teams=pending_teams,
                           username=username)


# 用户注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
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


# 更改用户信息
@app.route('/user_setting', methods=['GET', 'POST'])
@login_required
def user_setting():
    if request.method == 'POST':
        current_user.username = request.form['username']
        current_user.phone = request.form['phone']
        current_user.id_code = request.form.get('id_code', '')
        current_user.gender = request.form.get('gender', '')
        current_user.character = request.form.get('character', '')
        current_user.residence = request.form.get('residence', '')
        current_user.travel_hobby = request.form.get('travel_hobby', '')
        db.session.commit()
        return jsonify({'message': '用户信息已更新'}), 200

    return render_template('page/user_setting.html')


# 修改用户密码
@app.route('/user_password', methods=['GET', 'POST'])
@login_required
def user_password():
    if request.method == 'POST':
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        again_password = request.form['again_password']

        # Check if old password is correct
        if current_user.password != old_password:
            return jsonify({'message': '旧的密码不正确'}), 400

        # Check if new passwords match
        if new_password != again_password:
            return jsonify({'message': '两次输入的新密码不一致'}), 400

        # Update password in the database
        current_user.password = new_password
        db.session.commit()
        return jsonify({'message': '密码已更新'}), 200

    return render_template('page/user_password.html')


# 创建队伍
@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamForm()
    user = current_user
    if form.validate_on_submit():
        team = Team(
            destination=form.destination.data,
            departure_location=form.departure_location.data,
            travel_mode=form.travel_mode.data,
            team_type=form.team_type.data,
            travel_time=form.travel_time.data,
            travel_budget=form.travel_budget.data,
            max_members=form.max_members.data,
            current_members=1,  # 创建时包含队伍创建者
            public_id=user.id,  # 记录队伍创建者
            admin_id=user.id,  # 初始化管理员为队伍创建者
            travel_plan=None  # 初始化旅行计划
        )
        db.session.add(team)
        db.session.flush()  # 刷新 session 以获取新创建的 team.id

        # 将队伍创建者加入到队伍中, 并设置 audit_status 为 1
        db.session.execute(
            text(
                'INSERT INTO user_team (team_id, join_user_id, audit_status) VALUES (:team_id, :user_id, :audit_status)'),
            {'team_id': team.id, 'user_id': user.id, 'audit_status': 1}
        )
        # 更新队伍热度
        team.update_popularity()
        db.session.commit()
        flash('您的队伍已创建！', 'success')
        return redirect(url_for('my_manage_team'))
    return render_template('page/create_team.html', form=form)


# 发送的申请（发送申请界面）
@app.route('/sending_requests', methods=['GET', 'POST'])
def sending_requests():
    teams = Team.query.all()
    approved_teams = []
    pending_teams = []
    deny_teams = []
    username = current_user.username

    for team in teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
        else:
            deny_teams.append(team)

    return render_template('page/sending_requests.html', teams=teams, approved_teams=approved_teams,
                           pending_teams=pending_teams, deny_teams=deny_teams, username=username)


# 根据条件筛选队伍
@app.route('/search_teams', methods=['POST'])
@login_required
def search_teams():
    destination = request.form.get('destination', None)
    departure_location = request.form.get('departure_location', None)
    travel_mode = request.form.get('travel_mode', None)
    team_type = request.form.get('team_type', None)
    max_travel_budget = request.form.get('max_travel_budget', None)

    # 根据搜索条件查询队伍
    teams = Team.query.filter(
        Team.admin_id != current_user.id, Team not in current_user.teams)

    filters = []

    if destination:
        filters.append(Team.destination.ilike(f'%{destination}%'))

    if departure_location:
        filters.append(Team.departure_location.ilike(
            f'%{departure_location}%'))

    if travel_mode and travel_mode != '无要求':
        filters.append(Team.travel_mode == travel_mode)

    if team_type and team_type != '无要求':
        filters.append(Team.team_type == team_type)

    if max_travel_budget:
        filters.append(Team.travel_budget <= max_travel_budget)

    teams = teams.filter(and_(*filters)).all()

    return render_template('page/search_results.html', teams=teams)


# 加入队伍
@app.route('/join_team/<int:team_id>', methods=['POST'])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)
    user = current_user

    if team.current_members >= team.max_members:
        return jsonify({'status': 'error', 'message': '该队伍已满员。'})

    if team in user.teams:
        return jsonify({'status': 'error', 'message': '您已申请加入该队伍。'})

    # 更改实现逻辑，检查是否存在对应的申请记录
    membership = db.session.query(team_membership).filter_by(
        join_user_id=user.id, team_id=team.id).first()

    if membership:
        if membership.audit_status == 2:
            # 如果找到记录且 audit_status 为 2，则将其更新为 0
            stmt = team_membership.update().where(
                team_membership.c.join_user_id == user.id,
                team_membership.c.team_id == team_id
            ).values(audit_status=0)
            db.session.execute(stmt)
            # 队伍热度统计
            team.apply_count += 1
            team.update_popularity()
            db.session.commit()
            add_notification(
                team.admin_id, f"你收到一条来自 {current_user.username} 的入队申请。", url_for('team_requests'))
        else:
            return jsonify({'status': 'error', 'message': '您已经在该队伍中！'})
    else:
        # 如果没找到，则新增一条记录
        ins = team_membership.insert().values(
            join_user_id=user.id, team_id=team.id, audit_status=0)
        db.session.execute(ins)
        # 队伍热度统计
        team.apply_count += 1
        team.update_popularity()
        db.session.commit()
        add_notification(
            team.admin_id, f"你收到一条来自 {current_user.username} 的入队申请。", url_for('team_requests'))

    return jsonify({'status': 'success', 'message': '成功向队伍管理员发送入队申请'})


# 同意加入队伍申请
@app.route('/approve_request/<int:join_user_id>/<int:team_id>', methods=['POST'])
@login_required
def approve_request(join_user_id, team_id):
    team = Team.query.get_or_404(team_id)

    if team.admin_id != current_user.id:
        flash('您没有权限批准此请求。')
        return redirect(url_for('team_requests'))

    if team.current_members >= team.max_members:
        flash('无法批准请求，队伍已满员!')
        return redirect(url_for('team_requests'))

    # 更新申请状态为1（审核通过）
    stmt = team_membership.update().where(
        team_membership.c.join_user_id == join_user_id,
        team_membership.c.team_id == team_id
    ).values(audit_status=1)
    db.session.execute(stmt)
    team.current_members += 1
    # 更新队伍热度
    team.update_popularity()
    db.session.commit()

    add_notification(join_user_id, f"你的入队申请被 {current_user.username} 批准。", url_for(
        'sending_requests'))

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

    add_notification(join_user_id, f"你的入队申请被 {current_user.username} 拒绝。", url_for(
        'sending_requests'))

    flash('已成功拒绝入队申请！', 'success')
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
        # 将用户ID和队伍ID作为唯一标识符
        request_id = f"{request_info.join_user_id}-{request_info.team_id}"
        requests_dict[request_id] = {
            'username': request_info.username,
            'destination': request_info.destination,
            'join_user_id': request_info.join_user_id,
            'team_id': request_info.team_id
        }

    return render_template('page/team_requests.html', requests_dict=requests_dict)


# 用户登出
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# 主界面
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

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)

    return render_template('page/home.html',
                           teams=teams, approved_teams=approved_teams, pending_teams=pending_teams, username=username)


# 队伍成员查看队伍信息
@app.route('/team/<int:team_id>', methods=['GET'])
@login_required
def view_team(team_id):
    team = Team.query.get_or_404(team_id)
    approved_members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team_id,
        team_membership.c.audit_status == 1
    ).all()
    # 查询队伍目的地的前五个景点推荐
    city = team.destination
    top_attractions = (Attractions.query.filter(
        Attractions.城市 == city,
        Attractions.排名 != '0'
    ).order_by(
        cast(func.substring_index(Attractions.排名, '第', -1), Integer)
    ).limit(5).all())
    # 队伍热度更新
    team.view_count += 1
    team.update_popularity()
    db.session.commit()

    return render_template('page/view_team.html', team=team, approved_members=approved_members,
                           top_attractions=top_attractions)


@app.route('/teamfriend/<int:team_id>', methods=['GET'])
@login_required
def view_teamfriend(team_id):
    team = Team.query.get_or_404(team_id)
    approved_members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team_id,
        team_membership.c.audit_status == 1
    ).all()

    return render_template('page/view_teamfriend.html', team=team, approved_members=approved_members)


# 添加旅行计划
@app.route('/add_to_travel_plan', methods=['POST'])
def add_to_travel_plan():
    data = request.get_json()
    team_id = data.get('team_id')
    attraction_name = data.get('attraction_name')

    team = Team.query.get(team_id)
    if not team:
        return jsonify({'success': False, 'message': '队伍不存在'})

    # 获取当前的旅行计划，如果为 None，设为一个空字符串
    current_travel_plan = team.travel_plan or ''

    # 检查旅行计划中是否已经包含该景点名称
    if attraction_name in current_travel_plan:
        return jsonify({'success': False, 'message': '旅行计划中已包含该景点'})

    # 更新旅行计划
    if current_travel_plan:
        new_travel_plan = f"{current_travel_plan}，{attraction_name}"
    else:
        new_travel_plan = attraction_name

    team.travel_plan = new_travel_plan
    db.session.commit()

    return jsonify({'success': True})


# 退出队伍
@app.route('/leave_team/<int:team_id>', methods=['POST'])
@login_required
def leave_team(team_id):
    # 获取当前用户和队伍
    user = current_user
    team = Team.query.get_or_404(team_id)
    # 从数据库中查找用户与队伍的关联记录并删除
    user_team_record = team_membership.delete().where(
        (team_membership.c.join_user_id == user.id) &
        (team_membership.c.team_id == team_id) &
        (team_membership.c.audit_status == 1)
    )
    db.session.execute(user_team_record)
    db.session.commit()
    # 更新队伍中的成员数量
    team.current_members -= 1
    # 队伍热度更新
    team.update_popularity()
    db.session.commit()
    flash('成功退出队伍', 'success')

    add_notification(team.admin_id, f"成员 {current_user.username} 退出目的地为 {team.destination} 的队伍。", url_for(
        'view_teamfriend', team_id=team.id))

    # 重定向回到我的队伍页面或者其他适当的页面
    return redirect(url_for('my_join_team'))


# 管理的队伍界面
@app.route('/my_manage_team', methods=['GET'])
@login_required
def my_manage_team():
    teams = Team.query.all()
    approved_teams = []
    pending_teams = []

    for team in teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
    return render_template('page/my_manage_team.html', teams=teams, approved_teams=approved_teams,
                           pending_teams=pending_teams)


# 加入的队伍界面
@app.route('/my_join_team', methods=['GET'])
@login_required
def my_join_team():
    teams = Team.query.all()
    approved_teams = []
    pending_teams = []

    for team in teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1 and team.admin_id != current_user.id:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
    return render_template('page/my_join_team.html', teams=teams, approved_teams=approved_teams,
                           pending_teams=pending_teams)


def Search(user_id, destination=None, departure_location=None, travel_mode=None, team_type=None, max_travel_budget=None):
    conn = pymysql.connect(host='localhost',  # 主机
                           user='root',  # 用户
                           port=3306,  # 端口
                           password='123456',  # 密码
                           charset='utf8',  # 编码
                           database='lvu'  # 数据库名称
                           )

    cursor = conn.cursor()

    # 构建查询条件
    conditions = [
        "t.id NOT IN (SELECT ut.team_id FROM user_team ut WHERE ut.join_user_id = %s AND ut.audit_status = 1)"]
    params = [user_id]

    if destination:
        conditions.append("t.destination = %s")
        params.append(destination)
    if departure_location:
        conditions.append("t.departure_location = %s")
        params.append(departure_location)
    if travel_mode:
        conditions.append("t.travel_mode = %s")
        params.append(travel_mode)
    if team_type:
        conditions.append("t.team_type = %s")
        params.append(team_type)
    if max_travel_budget:
        conditions.append("t.travel_budget <= %s")
        params.append(max_travel_budget)

    # 生成 WHERE 子句
    where_clause = " AND ".join(conditions)

    # 查询数据库中的数据
    query = f"""
    SELECT t.id, t.popularity, t.destination, t.departure_location, t.travel_mode, t.team_type, t.travel_time, t.travel_budget, t.max_members, t.current_members
    FROM team t
    WHERE {where_clause}
    """

    cursor.execute(query, params)
    rows = cursor.fetchall()

    # 组织数据格式
    data = []
    for row in rows:
        data.append({
            "id": row[0],
            "popularity": row[1],
            "destination": row[2],
            "departure_location": row[3],
            "travel_mode": row[4],
            "team_type": row[5],
            "travel_time": row[6],
            "travel_budget": row[7],
            "max_members": row[8],
            "current_members": row[9]
        })

    # 创建最终的JSON结构
    result = {
        "code": 0,
        "msg": "",
        "count": len(data),
        "data": data
    }

    # 将结果写入JSON文件
    with open('static/api/table.json', 'w', encoding='utf-8') as json_file:
        json.dump(result, json_file, ensure_ascii=False, indent=4)

    # 关闭数据库连接
    conn.close()


# 可加入队伍界面
@app.route('/joinable_teams', methods=['GET'])
@login_required
def joinable_teams():
    destination = request.args.get('destination')
    departure_location = request.args.get('departure_location')
    travel_mode = request.args.get('travel_mode')
    team_type = request.args.get('team_type')
    max_travel_budget = request.args.get('max_travel_budget')
    teams = Team.query.all()
    approved_teams = []
    pending_teams = []
    username = current_user.username

    for team in teams:
        membership = db.session.query(team_membership).filter_by(
            join_user_id=current_user.id, team_id=team.id).first()

        if membership is None:
            continue  # 如果 membership 为空，跳过当前团队的处理

        if membership.audit_status == 1:
            approved_teams.append(team)
        elif membership.audit_status == 0:
            pending_teams.append(team)
    Search(user_id=current_user.id, destination=destination, departure_location=departure_location,
           travel_mode=travel_mode, team_type=team_type, max_travel_budget=max_travel_budget)

    return render_template('page/joinable_teams.html', teams=teams, approved_teams=approved_teams,
                           pending_teams=pending_teams, username=username)


# 管理员更改队伍信息
@app.route('/manage_team/<int:team_id>', methods=['GET', 'POST'])
@login_required
def manage_team(team_id):
    team = Team.query.get_or_404(team_id)

    if team.admin_id != current_user.id:
        return redirect(url_for('my_manage_team'))

    form = ManageTeamForm(obj=team)

    if form.validate_on_submit():
        if form.max_members.data < team.current_members:  # 判断设置的最大人数是否小于当前队伍中的人数
            flash(
                f'无法将队伍的最大人数设置为{form.max_members.data}，因为它小于当前的队伍人数 {team.current_members}.',
                'danger')
        else:
            form.populate_obj(team)  # 使用表单数据更新队伍对象
            db.session.commit()
            flash('成功更新队伍信息！', 'success')

            members = db.session.query(User).join(team_membership).filter(
                team_membership.c.team_id == team.id,
                team_membership.c.audit_status == 1
            ).all()
            # 给队伍成员发送队伍信息更新的通知
            for member in members:
                if member.id != team.admin_id:
                    add_notification(member.id, f"前往 {team.destination} 的队伍信息被管理员更新，请查看。", url_for(
                        'view_teamfriend', team_id=team.id))

        return redirect(url_for('manage_team', team_id=team.id))

    # 只获取审核通过的成员
    members = db.session.query(User).join(team_membership).filter(
        team_membership.c.team_id == team.id,
        team_membership.c.audit_status == 1
    ).all()

    return render_template('page/manage_team.html', team=team, form=form, members=members)


@app.route('/manage_team/update', methods=['POST'])
def update_team():
    team_id = request.form.get('id')
    destination = request.form.get('destination')
    departure_location = request.form.get('departure_location')
    travel_mode = request.form.get('travel_mode')
    team_type = request.form.get('team_type')
    travel_time = request.form.get('travel_time')
    travel_budget = request.form.get('travel_budget')
    max_members = request.form.get('max_members')

    # 根据 team_id 查询数据库中的队伍记录
    team = Team.query.get(team_id)
    if not team:
        return 'Team not found', 404

    # 更新队伍信息
    team.destination = destination
    team.departure_location = departure_location
    team.travel_mode = travel_mode
    team.team_type = team_type
    team.travel_time = travel_time
    team.travel_budget = travel_budget
    team.max_members = max_members

    db.session.commit()
    return 'Team updated successfully'


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
        # 队伍热度更新
        team.update_popularity()
        db.session.commit()
        flash('成员已成功移除！', 'success')
        add_notification(
            user.id, f"你被移出前往 {team.destination} 的队伍。", url_for('view_teamfriend', team_id=team.id))

    return redirect(url_for('manage_team', team_id=team_id))


# 管理员移交管理员权限
@app.route('/transfer_admin/<int:team_id>/<int:user_id>', methods=['POST'])
@login_required
def transfer_admin(team_id, user_id):
    team = Team.query.get_or_404(team_id)
    if team.admin_id != current_user.id:
        return redirect(url_for('manage_team', team_id=team.id))

    new_admin = User.query.get_or_404(user_id)
    if new_admin not in team.members:
        flash('此用户不是该队伍的成员。', 'danger')
        return redirect(url_for('manage_team', team_id=team.id))

    team.admin_id = new_admin.id
    db.session.commit()

    flash(f'管理员权限已转移给 {new_admin.username}.', 'success')
    add_notification(
        new_admin.id, f"你已被设为前往 {team.destination} 的队伍的管理员。", url_for('my_manage_team'))
    return redirect(url_for('manage_team', team_id=team.id))


# 邀请用户入队
@app.route('/invite_user', methods=['POST'])
@login_required
def invite_user():
    data = request.get_json()
    username = data.get('username')
    team_id = data.get('team_id')
    team = Team.query.get_or_404(team_id)

    if not username or not team_id:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    invitee = User.query.filter_by(username=username).first()

    if not invitee:
        return jsonify({'success': False, 'message': '用户不存在'}), 404

    # 检查是否邀请自己
    if invitee.id == current_user.id:
        return jsonify({'success': False, 'message': '不能邀请自己加入队伍'})

    # 检查用户是否已经在队伍中
    membership = db.session.query(team_membership).filter_by(
        join_user_id=invitee.id, team_id=team.id, audit_status=1).first()
    if membership:
        return jsonify({'success': False, 'message': '用户已在队伍中，无法再次邀请'})

    # 检查队伍是否已满
    if team.current_members >= team.max_members:
        return jsonify({'success': False, 'message': '队伍人数已满，无法邀请更多成员'})

    # 创建邀请
    invitation = Invitation(
        team_id=team_id,
        inviter_id=current_user.id,
        invitee_id=invitee.id,
        status='pending'
    )
    db.session.add(invitation)
    db.session.commit()

    add_notification(invitee.id, f"你收到来自 {current_user.username} 的入队邀请。", url_for(
        'received_invitations'))

    return jsonify({'success': True, 'message': '邀请已发送'})


# 收到的邀请界面
@app.route('/received_invitations', methods=['GET'])
@login_required
def received_invitations():
    user_id = current_user.id
    invitations = Invitation.query.filter_by(invitee_id=user_id).all()

    return render_template('page/received_invitations.html', invitations=invitations)


# 发送的邀请界面
@app.route('/sent_invitations')
@login_required
def sent_invitations():
    invitations = Invitation.query.filter_by(inviter_id=current_user.id).all()
    return render_template('page/sent_invitations.html', invitations=invitations)


# 处理收到的入队邀请
@app.route('/handle_invitation', methods=['POST'])
@login_required
def handle_invitation():
    data = request.json
    invitation_id = data.get('invitation_id')
    action = data.get('action')

    if not invitation_id or not action:
        return jsonify({'success': False, 'message': '缺少参数'}), 400

    invitation = Invitation.query.get(invitation_id)

    if not invitation:
        return jsonify({'success': False, 'message': '邀请不存在'}), 404

    if action == 'accept':
        team_id = invitation.team_id
        invitee_id = invitation.invitee_id
        inviter_id = invitation.inviter_id
        team = Team.query.get(team_id)

        if team.admin_id == inviter_id:
            # 直接加入队伍
            membership = db.session.query(team_membership).filter_by(
                join_user_id=invitee_id, team_id=team.id).first()

            if membership:
                if membership.audit_status == 2 or membership.audit_status == 0:
                    # 如果找到记录且 audit_status 为 2 或 0，则将其更新为 1
                    stmt = team_membership.update().where(
                        team_membership.c.join_user_id == invitee_id,
                        team_membership.c.team_id == team.id
                    ).values(audit_status=1)
                    db.session.execute(stmt)

                    team.current_members += 1
                else:
                    flash('您已经在该队伍中！')
            else:
                # 如果没找到，则新增一条记录
                ins = team_membership.insert().values(
                    join_user_id=invitee_id, team_id=team_id, audit_status=1)
                db.session.execute(ins)
                team.current_members += 1

            invitation.status = 'accepted'
            add_notification(
                inviter_id, f"你的邀请被 {current_user.username} 接受了。", url_for('sent_invitations'))
            # 队伍热度更新
            team.update_popularity()
            db.session.commit()
            return jsonify({'success': True, 'message': '邀请已接受'})
        else:
            membership = db.session.query(team_membership).filter_by(
                join_user_id=invitee_id, team_id=team.id).first()

            if membership:
                if membership.audit_status == 2:
                    # 如果找到记录且 audit_status 为 2，则将其更新为 0
                    stmt = team_membership.update().where(
                        team_membership.c.join_user_id == invitee_id,
                        team_membership.c.team_id == team.id
                    ).values(audit_status=0)
                    db.session.execute(stmt)
                else:
                    flash('您已经在该队伍中！')
            else:
                # 如果没找到，则新增一条记录
                ins = team_membership.insert().values(
                    join_user_id=invitee_id, team_id=team_id, audit_status=0)
                db.session.execute(ins)

            invitation.status = 'accepted'
            add_notification(
                inviter_id, f"你的邀请被 {current_user.username} 接受了。", url_for('sent_invitations'))
            db.session.commit()
            return jsonify({'success': True, 'message': '邀请已接受！\n已成功向队伍管理员发送入队申请'})

    elif action == 'decline':
        invitation.status = 'declined'
        add_notification(invitation.inviter_id, f"你的邀请被 {current_user.username} 拒绝了。", url_for(
            'sent_invitations'))
        db.session.commit()
        return jsonify({'success': True, 'message': '邀请已拒绝'})

    return jsonify({'success': False, 'message': '无效的操作'}), 400


# 新增通知消息
def add_notification(user_id, message, link=None):
    notification = Notification(user_id=user_id, message=message, link=link)
    db.session.add(notification)
    db.session.commit()


# 消息通知界面
@app.route('/notifications')
@login_required
def notifications():
    notifications_ = Notification.query.filter_by(
        user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    return render_template('page/notifications.html', notifications=notifications_)


# 更新消息阅读状态
@app.route('/mark_as_read', methods=['POST'])
@login_required
def mark_as_read():
    data = request.get_json()
    notification_id = data.get('notification_id')
    notification = Notification.query.get_or_404(notification_id)

    if notification.user_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限标记此通知为已读'}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({'success': True, 'message': '消息已标记为已读'})


if __name__ == '__main__':
    app.run(debug=True)
