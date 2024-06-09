from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, SelectField, TextAreaField
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
    travel_budget = IntegerField('旅游预算', validators=[DataRequired(), NumberRange(min=0)])
    max_members = IntegerField('最大人数', validators=[DataRequired(), NumberRange(min=1, message="至少为1人")])
    submit = SubmitField('创建队伍')


class ManageTeamForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    departure_location = StringField('Departure Location', validators=[DataRequired()])
    travel_mode = StringField('Travel Mode')
    team_type = StringField('Team Type')
    travel_time = StringField('Travel Time', validators=[DataRequired()])
    travel_budget = IntegerField('Travel Budget', validators=[DataRequired(), NumberRange(min=0)])
    max_members = IntegerField('Max Members',
                               validators=[DataRequired(), NumberRange(min=1, message="人数至少为1")])
    submit = SubmitField('Update Team')


class UserForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    phone = StringField('手机号', validators=[DataRequired()])
    id_code = StringField('身份证号')
    gender = SelectField('性别', choices=[('', '请选择性别'), ('male', '男'), ('female', '女'), ('other', '其他')])
    character = StringField('性格')
    residence = StringField('居住地')
    travel_hobby = TextAreaField('旅游爱好')
    submit = SubmitField('确认保存')
