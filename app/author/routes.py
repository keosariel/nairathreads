from flask import (
    flash, 
    redirect, 
    render_template, 
    request, 
    url_for,
    current_app,
    abort
)

from flask_login import login_required, current_user
from app.author.forms import EditProfileForm

from app import db
from app.author import author
from app.models import (
    Post, 
    Group, 
    User, 
    Hide,
    Vote,
    Favourite
)


@author.route('/u/<string:username>',methods=['GET'])
def profile(username):
    username = username.lower().strip()
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            if current_user == user and current_user.is_authenticated:
                return render_template("profile.html",title="Profile",tab="profile",user=user,pagename=f"{user.username}'s profile")
            else:
                return render_template("user.html",title="Profile",tab="profile",user=user,pagename=f"{user.username}'s profile")
    return abort(404)


@author.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username, current_user.email)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.bio = form.bio.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your changes have been saved.","success")
        return redirect(url_for("author.profile", username=current_user.username))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.bio.data = current_user.bio
        form.email.data = current_user.email
    return render_template(
        "edit_profile.html", 
        title="Edit Profile", 
        tab="edit profile",
        form=form,
        user=current_user
    )


@author.route("/submitted", methods=["GET","POST"])
def submitted():
    page = request.args.get("page", 1, type=int)
    username = request.args.get("id", None, type=str)
    
    if username:
        author = User.query.filter_by(username=username).first()
        if author:
            posts =(
                Post.query.filter_by(parent_id=0,user_id=author.id)
                .order_by(Post.date.desc())
                .paginate(page, 30, True)
            )
            
            next_url = (
                url_for("author.submitted",id=username,page=posts.next_num) if posts.has_next else None
            )
            start_rank_num = 30 * (page - 1) + 1
            
            #add_posts()
            return render_template(
                    "home.html",
                    pagename=f"{author.username}'s submissions",
                    tab="submitted",
                    posts=posts.items,
                    start_rank_num=start_rank_num,
                    next_url=next_url,
                    title="Submitted"
                )
        
    return abort(404)

@author.route("/comments", methods=["GET","POST"])
def comments():
    page = request.args.get("page", 1, type=int)
    username = request.args.get("id", None, type=str)
    
    if username:
        author = User.query.filter_by(username=username).first()
        if author:
            posts =(
                Post.query.filter_by(user_id=author.id)
                .filter(Post.parent_id > 0)
                .order_by(Post.date.desc())
                .paginate(page, 30, True)
            )
            
            next_url = (
                url_for("author.comments",id=username,page=posts.next_num) if posts.has_next else None
            )
            start_rank_num = 30 * (page - 1) + 1
            
            #add_posts()
            return render_template(
                    "newcomments.html",
                    pagename=f"{author.username}'s comments",
                    tab="comments",
                    posts=posts.items,
                    start_rank_num=start_rank_num,
                    next_url=next_url,
                    title=f"{author.username}'s comments"
                )
        
    return abort(404)

@author.route("/hidden", methods=["GET","POST"])
@login_required
def hidden():
    page = request.args.get("page", 1, type=int)
    
    hidden = (
        Hide.query.filter_by(user_id=current_user.id)
        .order_by(Hide.date.desc())
        .paginate(page, 30, True)
    )
    
    hidden_items = hidden.items
    hidden_posts = []
    
    for hi in hidden_items:
        hidden_posts.append(hi.post)
    
    next_url = (
        url_for("author.hidden", page=hidden.next_num) if hidden.has_next else None
    )
    start_rank_num = 30 * (page - 1) + 1
    
    return render_template(
            "home.html",
            pagename=f"{current_user.username}'s hidden",
            tab="hidden",
            posts=hidden_posts,
            start_rank_num=start_rank_num,
            next_url=next_url,
            title="Hidden")


@author.route("/upvoted", methods=["GET","POST"])
@login_required
def upvoted():
    page = request.args.get("page", 1, type=int)
    username = request.args.get("id", None, type=str)
    comments = request.args.get("comments", None, type=str)
    
    if username == current_user.username:
        voted = (
            Vote.query.filter_by(user_id=current_user.id,state=1,flag=0)
            .order_by(Vote.date.desc())
            .paginate(page, 30, True)
        )
        
        voted_items = voted.items
        voted_posts = []
        
        for vi in voted_items:
            voted_posts.append(vi.post)
        
        next_url = (
            url_for("author.upvoted",id=username,page=voted.next_num) if voted.has_next else None
        )
        start_rank_num = 30 * (page - 1) + 1
        
        return render_template(
                "home.html",
                pagename=f"{current_user.username}'s upvoted",
                tab="upvoted",
                posts=voted_posts,
                start_rank_num=start_rank_num,
                next_url=next_url,
                title="Upvoted")
    
    return abort(404)


@author.route("/favorites", methods=["GET","POST"])
def favorites():
    page = request.args.get("page", 1, type=int)
    username = request.args.get("id", None, type=str)
    
    if username:
        author = (
            User.query.filter_by(username=username)
            .first()
        )
        if author:
            favorites = (
                Favourite.query.filter_by(user_id=author.id,state=1)
                .order_by(Favourite.date.desc())
                .paginate(page, 30, True)
            )
            
            favorite_items = favorites.items
            favorite_posts = []
            
            for vi in favorite_items:
                favorite_posts.append(vi.post)
            
            next_url = (
                url_for("author.favorites",id=username,page=favorites.next_num) if favorites.has_next else None
            )
            start_rank_num = 30 * (page - 1) + 1
            
            return render_template(
                    "home.html",
                    pagename=f"{author.username}'s favourites",
                    posts=favorite_posts,
                    tab="favorites",
                    start_rank_num=start_rank_num,
                    next_url=next_url,
                    title="Favorites")
        
    return abort(404)
