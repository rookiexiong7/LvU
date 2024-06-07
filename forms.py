from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TeamForm(FlaskForm):
    destination = StringField('目的地', validators=[DataRequired()])
    departure_location = StringField('出发地点', validators=[DataRequired()])
    travel_mode = StringField('出行方式', validators=[DataRequired()])
    team_type = StringField('队伍类型', validators=[DataRequired()])
    travel_time = StringField('游玩时间', validators=[DataRequired()])
    travel_budget = StringField('旅游预算', validators=[DataRequired()])
    max_members = IntegerField('最大人数', validators=[DataRequired()])
    submit = SubmitField('创建队伍')


class ManageTeamForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    max_members = IntegerField('Max Members',
                               validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1")])
    submit = SubmitField('Update Team')
