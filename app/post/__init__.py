from flask import Blueprint

post = Blueprint("post", __name__)

from app.post import routes