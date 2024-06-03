from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, NumberRange


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TeamForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    max_members = IntegerField('Max Members', validators=[DataRequired()])
    submit = SubmitField('Create Team')


class ManageTeamForm(FlaskForm):
    destination = StringField('Destination', validators=[DataRequired()])
    max_members = IntegerField('Max Members',
                               validators=[DataRequired(), NumberRange(min=1, message="Must be at least 1")])
    submit = SubmitField('Update Team')
