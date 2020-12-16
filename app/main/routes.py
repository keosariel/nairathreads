from flask import (
    render_template, 
    url_for, 
    flash, 
    redirect, 
    request, 
    abort,
    current_app
)

from flask_login import login_required, current_user
from . import main

from app.models import (
    Post,
    Group,
    User,
    Member
)

from app.utils import add_posts,Index
from threading import Thread
from app import db
from datetime import datetime

GLOBAL_INDEX = Index()
UPDATE_SCORE = datetime.utcnow()

@main.route('/',methods=['GET','POST'])
@main.route("/home", methods=["GET","POST"])
def home():
    return redirect(url_for('main.top'))

@main.route("/top", methods=["GET","POST"])
def top():
    global UPDATE_SCORE
    datetime_difference = datetime.utcnow() - UPDATE_SCORE
    hours = datetime_difference.seconds / 3600
    
    if hours >= 0.5:
        print("UPDATING SCORE")
        UPDATE_SCORE = datetime.utcnow()  
        # TODO optimize this rendering
        for post in Post.query.filter_by(deleted=0,parent_id=0).all():
            post.update_score()
        db.session.commit()
        
    page = request.args.get("page", 1, type=int)
    posts =(
        Post.query.filter_by(deleted=0,parent_id=0)
        .order_by(Post.score.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.top", page=posts.next_num) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    #add_posts()
    return render_template(
            "home.html",
            _pagename="all",
            tab="top",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="Top")

@main.route("/new", methods=["GET","POST"])
def new():
    page = request.args.get("page", 1, type=int)
    posts =(
        Post.query.filter_by(deleted=0,parent_id=0)
        .order_by(Post.date.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.new", page=posts.next_num) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    #add_posts()
    return render_template(
            "home.html",
            _pagename="all",
            tab="new",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="New")
    
@main.route("/newcomments", methods=["GET","POST"])
def newcomments():
    page = request.args.get("page", 1, type=int)
    posts =(
        Post.query.filter_by(deleted=0)
        .filter(Post.parent_id > 0)
        .order_by(Post.date.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.newcomments", page=posts.next_num) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    return render_template(
            "newcomments.html",
            _pagename="new comments",
            tab="newcomments",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="New comments")


@main.route("/ask", methods=["GET","POST"])
def ask():
    page = request.args.get("page", 1, type=int)
    posts =(
        Post.query.filter_by(deleted=0)
        .filter(Post.title.startswith("Ask NT:"))
        .order_by(Post.date.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.ask", page=posts.next_num) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    return render_template(
            "home.html",
            _pagename="ask",
            tab="ask",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="Ask")

@main.route("/job", methods=["GET","POST"])
def job():
    page = request.args.get("page", 1, type=int)
    posts =(
        Post.query.filter_by(deleted=0)
        .filter(Post.title.startswith("Job:"))
        .order_by(Post.date.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.job", page=posts.next_num) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    return render_template(
            "home.html",
            _pagename="job",
            tab="job",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="Jobs")

@main.route("/search", methods=["GET","POST"])
def search():
    global GLOBAL_INDEX
    Thread(
        target=GLOBAL_INDEX.add_to_index, 
        args=([(post.title,post.id) for post in Post.query.filter(Post.parent_id==0,Post.deleted==0).all()],)
    ).start()

    query = request.args.get("q", "", type=str)
    page = request.args.get("page", 1, type=int)
    
    posts_ids = GLOBAL_INDEX.search(query.lower().strip())

    start_rank_num = 30 * (page - 1) + 1
    
    next_num = None
    
    if (30 * page) < len(posts_ids):
        next_num = page + 1
    
    next_url = (
        url_for("main.search", page=next_num,q=query) if next_num else None
    )
    
    posts = []
    for post_id in posts_ids[30 * (page-1) : (30 * (page-1)) + 30]:
        post = Post.query.get(post_id)
        if post:
            posts.append(post)
    
    return render_template(
            "search.html",
            pagename="search",
            tab="search",
            posts=posts,
            start_rank_num=start_rank_num,
            next_url=next_url,
            query=query,
            title="Search")

@main.route("/from", methods=["GET","POST"])
def site():
    query = request.args.get("site", "", type=str)
    query = query.strip()
    page = request.args.get("page", 1, type=int)
    
    posts =(
        Post.query.filter_by(deleted=0,parent_id=0)
        .filter(Post.url_base==query)
        .order_by(Post.date.desc())
        .paginate(page, 30, True)
    )
    
    next_url = (
        url_for("main.site", page=posts.next_num, site=query) if posts.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    #add_posts()
    return render_template(
            "home.html",
            pagename=f"from ({query})",
            tab="site",
            posts=posts.items,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="Site")
    
@main.route("/about", methods=["GET"])
def about():
    return render_template(
            "about.html",
            pagename=f"About",
            tab="about",
            title="About")
    
@main.route("/privacy", methods=["GET"])
def privacy():
    return render_template(
            "privacy.html",
            pagename=f"Privacy",
            tab="privacy",
            title="Privacy")

@main.route("/rules", methods=["GET"])
def rules():
    return render_template(
            "rules.html",
            pagename=f"Rules",
            tab="rules",
            title="Rules")
    
@main.route("/anonymous", methods=["GET"])
def anonymous():
    return render_template(
            "anonymous.html",
            pagename=f"Anonymous",
            tab="anonymous",
            title="Anonymous")