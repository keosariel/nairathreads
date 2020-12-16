from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import (
    ValidationError,
    DataRequired,
    Email,
    Length,
    URL,
    Optional,
)

class PostForm(FlaskForm):
    title = StringField(
        "Title", validators=[DataRequired(), Length(min=9, max=250)]
    )
    text = TextAreaField(
        "Text", validators=[Optional(), Length(min=2)]
    )
    url = StringField("url", validators=[Optional(), URL()])
    
    #group = SelectField("Group",choices=[(0,"osos"),(1,"sjnd")],validators=[Optional(), URL()])
    submit = SubmitField("Submit")
    

    
class CommentForm(FlaskForm):
    text = TextAreaField(
        "Comment Text", validators=[DataRequired(), Length(min=2, max=280)]
    )
    parent_id = StringField("Parent", validators=[DataRequired()])
    submit = SubmitField("Add Comment")