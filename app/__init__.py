from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from app.config import Config
from flask_mail import Mail

#db sqlite:///site.db
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info' #bootstrap class
mail = Mail()

def create_db():
    global db
    db.create_all()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    
    from app.admin import admin
    from app.auth import auth
    from app.main import main
    from app.post import post
    from app.errors import errors
    from app.author import author
    app.register_blueprint(admin)
    app.register_blueprint(auth)
    app.register_blueprint(post)
    app.register_blueprint(main)
    app.register_blueprint(author)
    app.register_blueprint(errors)

    return app

from app import models