from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
import re

USERNAME_REG = re.compile("^[A-Za-z0-9][A-Za-z0-9_]+")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")
    
    def validate_username(self, username):
        global USERNAME_REG
        _username = username.data.strip()
        if len(_username) < 2:
            raise ValidationError("Username must be at least two (2) characters.")
        elif len(_username) > 15:
            raise ValidationError("Username must be at least two (2) and at most (15) characters.")
        elif _username.startswith("_"):
            raise ValidationError("Username cannot start with an *underscore* ( _ )")
        
        if not USERNAME_REG.fullmatch(_username):
            raise ValidationError("Username can only contain characters A-Z, a-z and 0-9.")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign up")

    def validate_username(self, username):
        global USERNAME_REG
        _username = username.data.strip()
        if len(_username) < 2:
            raise ValidationError("Username must be at least two (2) characters.")
        elif len(_username) > 15:
            raise ValidationError("Username must be at least two (2) and at most (15) characters.")
        elif _username.startswith("_"):
            raise ValidationError("Username cannot start with an *underscore* ( _ )")
        
        if USERNAME_REG.fullmatch(_username):
            user = User.query.filter_by(username=_username).first()
            if user is not None:
                raise ValidationError("Username already exists.")
        else:
            raise ValidationError("Username can only contain characters A-Z, a-z and 0-9.")

    def validate_password(self, password):
        _password = password.data.strip()
        
        if len(_password) < 8:
            raise ValidationError("Password must be at least eight (8) characters")
        
class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Reset Password")
    
    def validate_email(self, email):
        if email.data:
            user = User.query.filter_by(email=email.data).first()
            if user is None:
                raise ValidationError("Sorry there is no account with this email.")



class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request Password Reset")
    
    def validate_password(self, password):
        _password = password.data.strip()
        
        if len(_password) < 8:
            raise ValidationError("Password must be at least eight (8) characters")


class ChangePasswordForm(FlaskForm):
    password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired()])
    confirm_new_password = PasswordField("Confirm New Password", validators=[DataRequired(),EqualTo("new_password")])
    submit = SubmitField("change")
    
    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user
        
    def validate_password(self, password):
        if not self.user.check_password(password.data):
            raise ValidationError("password is incorrect.")
        
    def validate_new_password(self, password):
        _password = password.data.strip()
        
        if len(_password) < 8:
            raise ValidationError("Password must be at least eight (8) characters")

    