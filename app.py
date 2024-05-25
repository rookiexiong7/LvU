from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from forms import RegistrationForm, LoginForm, TeamForm
from models import db, User, Team

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route('/create_team', methods=['GET', 'POST'])
@login_required
def create_team():
    form = TeamForm()
    if form.validate_on_submit():
        team = Team(destination=form.destination.data, max_members=form.max_members.data, admin=current_user)
        db.session.add(team)
        db.session.commit()
        flash('Your team has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_team.html', form=form)

@app.route('/join_team/<int:team_id>', methods=['POST'])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)
    if team.current_members < team.max_members:
        team.current_members += 1
        db.session.commit()
        flash('You have joined the team!', 'success')
    else:
        flash('The team is full!', 'danger')
    return redirect(url_for('home'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    teams = Team.query.filter_by(admin_id=current_user.id).all()
    return render_template('admin_dashboard.html', teams=teams)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@app.route('/home')
def home():
    teams = Team.query.all()
    return render_template('home.html', teams=teams)

if __name__ == '__main__':
    app.run(debug=True)
