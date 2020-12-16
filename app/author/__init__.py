from flask import Blueprint

author = Blueprint("author", __name__)

from app.author import routes