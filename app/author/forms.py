from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField,PasswordField
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    Length,
    URL,
    Optional,
)
from app.models import User,Group
import re

USERNAME_REG = re.compile("^[A-Za-z0-9][A-Za-z0-9_]+")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    bio = TextAreaField("About me", validators=[Length(min=0, max=140)])
    email = StringField("Email", validators=[Optional(),Email()])
    submit = SubmitField("Submit")

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        global USERNAME_REG        
        if username.data != self.original_username:
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


    def validate_email(self, email):
        if email.data:
            if email.data != self.original_email:
                user = User.query.filter_by(email=self.email.data).first()
                if user is not None:
                    raise ValidationError("Please use a different email.")