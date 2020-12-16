from app.custom_encrypt import create_map
import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

    ENDOCE_MAP, DECODE_MAP = create_map(SECRET_KEY) 
    ENCODE_COUNT = 3
    
    MAIL_ADMIN_ADDRESS = os.environ.get("MAIL_ADMIN_ADDRESS")
    MAIL_SERVER =  os.environ.get("MAIL_SERVER")
    MAIL_PORT = 465
    MAIL_USE_TLS=False
    MAIL_USE_SSL=True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    
    POSTS_PER_PAGE = 30