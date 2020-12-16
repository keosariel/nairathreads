from flask import (
    flash, 
    redirect, 
    render_template, 
    request, 
    url_for,
    current_app,
    abort
)

from flask_login import current_user
from . import admin

from app.models import (
    Post, 
    User, 
    Flag
)

from app.utils import is_admin

@admin.route('/admin',methods=['GET'])
def admin_panel():
    if not current_user.is_authenticated:
        return abort(404)
    
    if current_user.is_admin():
        users = User.query.all()
        posts = Post.query.all()
        flagged = (
            Post.query.filter(Post.flagged > 0)
            .all()
        )
        
        return render_template(
            "admin.html",
            title="Admin panel", 
            tab="admin",
            users=users,
            posts=posts,
            flagged=flagged
        )
    
    return abort(404)
    
@admin.route('/u',methods=['GET'])
def users():
    page = request.args.get("page", 1, type=int)
    
    if not current_user.is_authenticated:
        return abort(404)
    
    if current_user.is_admin():
        users = User.query.paginate(page, 30, True)
        
        next_url = (
            url_for("admin.users",page=users.next_num) if users.has_next else None
        )
        
        start_rank_num = 30 * (page - 1) + 1
        
        return render_template(
            "users.html",
            title="Users", 
            tab="users",
            users=users.items,
            next_url=next_url
        )
    return abort(404)
    
@admin.route('/f',methods=['GET'])
def flagged():
    page = request.args.get("page", 1, type=int)
    
    if not current_user.is_authenticated:
        return abort(404)
    
    if current_user.is_admin():
        posts = (
            Post.query.filter(Post.flagged > 0)
            .paginate(page, 30, True)
        )
        
        next_url = (
            url_for("admin.users",page=posts.next_num) if posts.has_next else None
        )
        
        start_rank_num = 30 * (page - 1) + 1
        
        return render_template(
            "home.html",
            title="Users", 
            tab="users",
            posts=posts.items,
            next_url=next_url,
            start_rank_num=start_rank_num
        )
    return abort(404)
    