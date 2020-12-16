from app import db,login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import case, text

from urllib.parse import urlparse
from markdown import markdown
import bleach

import jwt
from time import time

from datetime import datetime as dt
from datetime import datetime


def sanitize(text):
    if not text:
        return ""
    html = markdown(text)
    allowed_tags = ["a", "abbr", "acronym", "b", "blockquote", 
                    "code", "em", "i", "li", "ol", "strong","ul",
                    "strong","pre","p","u","strike","h4","h5","h6","u"]
    attr = {"a": ["href", "rel"]}
    html = bleach.clean(html,
        tags = allowed_tags,
        strip_comments=True,
        strip=True,
        protocols=["http", "https", "mailto"],
        styles=[],
        attributes=attr
    )
    
    html = bleach.linkify(html)
    return html.strip()
    

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text, nullable=True)
    username = db.Column(db.String(30), nullable=False)
    firstname = db.Column(db.String(30), nullable=True)
    lastname = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100),unique=True, nullable=True)
    password = db.Column(db.String(20), nullable=False)
    bio = db.Column(db.String(300), nullable=True)
    avatar = db.Column(db.Text, nullable=True)
    location = db.Column(db.Text, nullable=True)
    twitter = db.Column(db.Text, nullable=True)
    karma = db.Column(db.Integer, default=1)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    deleted = db.Column(db.Integer, default=0)
    posts = db.relationship('Post', backref='author', lazy=True)
    votes = db.relationship('Vote', backref='author', lazy=True)
    hides = db.relationship('Hide', backref='author', lazy=True)
    faves = db.relationship('Favourite', backref='author', lazy=True)
    flags = db.relationship('Flag', backref='author', lazy=True)
    groups = db.relationship('Group', backref='author', lazy=True)
    joined = db.relationship('Member', backref='author', lazy=True)
    roles = db.relationship('Role', backref='author', lazy=True)
    misc = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except Exception:
            return
        return User.query.get(id)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def is_admin(self):
        if self.username == "keosariel":
            return True
        return False
    
    def can_post(self):
        return True
    
    def can_create_group(self):
        time  = dt.utcnow()
        diff = time - self.timestamp
        daydiff = diff.days
        secdiff = diff.seconds
        
        if daydiff >= 7 and len(self.posts) >= 5 and bool(self.email):
            return True
        return False
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def __repr__(self):
        return f"User(username= {self.username}, email= {self.email})"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.Text, nullable=True)
    caption = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    url_base = db.Column(db.Text())
    body = db.Column(db.Text, nullable=True)
    views = db.Column(db.Integer, nullable=False, default=0)
    thumbnail = db.Column(db.Text, nullable=True)
    main_parent_id = db.Column(db.Integer, nullable=False)
    score = db.Column(db.Float, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_type = db.Column(db.Integer, nullable=False,default=0)
    flagged = db.Column(db.Integer, nullable=False,default=0) # if 1 then it has been deleted elif 2 drafted
    deleted = db.Column(db.Integer, default=0)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    path = db.Column(db.Text, index=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)    
    tags = db.relationship('Tag', backref='post', lazy=True)
    votes = db.relationship('Vote', backref='post', lazy=True)
    hides = db.relationship('Hide', backref='post', lazy=True)
    faves = db.relationship('Favourite', backref='post', lazy=True)
    flags = db.relationship('Flag', backref='post', lazy=True)
    misc = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def save(self):
        #with current_app.app_context():
        db.session.add(self)
        db.session.commit()
        
    def update_score(self, gravity=1.8):
        datetime_difference = datetime.utcnow() - self.date
        hours_passed = (
            datetime_difference.days * 24 + datetime_difference.seconds / 3600
        )
        
        votes = len(self.votes)
        votes = votes if votes > 0 else 1
        
        self.score = (votes - 1) / pow((hours_passed + 2), gravity)


    def is_deleted(self):
        if self.deleted != 0:
            return True
        return False
    
    def is_flagged(self):
        if self.deleted == 2:
            return True
        return False
            
    def get_text_as_html(self):
        html = sanitize(self.body)
        return html
    
    def can_delete(self):
        return True
    
    def __repr__(self):
        return f"Post(user={self.user_id},title= {self.title}, body= {self.body})"
  

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Tag(value= {self.value}, post_id= {self.post_id})"

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text, nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Vote(state= {self.state}, post_id= {self.post_id}, user_id= {self.author.id})"

class Hide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text, nullable=True)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Hide(post_id= {self.post_id})"

class Favourite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text, nullable=True)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Favourite(user_id={self.user_id}, post_id= {self.post_id})"
    

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    wiki = db.Column(db.Text, nullable=True)
    rules = db.Column(db.Text, nullable=True)
    flagged = db.Column(db.Integer, nullable=False,default=0) # if 1 then it has been deleted elif 2 drafted
    deleted = db.Column(db.Integer, default=0)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    posts = db.relationship('Post', backref='group', lazy=True)
    members = db.relationship('Member', backref='group', lazy=True)
    roles = db.relationship('Role', backref='group', lazy=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, default=0)
    misc = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def get_about(self):
        return sanitize(self.wiki)
    
    def get_rules(self):
        return sanitize(self.rules)
    
    def __repr__(self):
        return f"Group(user_id={self.user_id}, name= {self.name})"
    
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Member(user_id={self.user_id}, group_id= {self.group_id})"

    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    permission = db.Column(db.Integer, nullable=False, default=1)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Role(user_id={self.user_id}, group_id= {self.group_id}, permission= {self.permission})"
    
class Flag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.Text, nullable=True)
    state = db.Column(db.Integer, nullable=False, default=1)
    flag = db.Column(db.Integer, nullable=False, default=0)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Flag(user_id={self.user_id}, post_id= {self.post_id})"
    
