from flask import (
    render_template, 
    url_for, 
    flash, 
    redirect, 
    request, 
    abort,
    current_app,
    jsonify
)

from flask_login import login_required, current_user

from . import post
from app.post.forms import (
    CommentForm, 
    PostForm
    
)

from app.models import (
    Post,
    Group,
    User,
    Hide,
    Vote,
    Favourite,
    Flag
)

from app import db
from app.utils import add_posts, get_url_base, Index, is_admin
from app.custom_encrypt import custom_decode


@post.route('/item',methods=['GET','POST'])
def item():
    args = request.args
    if "id" in args:
        try:
            post_id = int(args["id"])
        except Exception as err:
            return abort(404)
        post = Post.query.get(post_id)
        hide,vote,fave = None,None,None

        if current_user.is_authenticated:
            hide = Hide.query.filter_by(post_id=post.id,user_id=current_user.id).first()
            vote = Vote.query.filter_by(post_id=post.id,user_id=current_user.id).first()
            fave = Favourite.query.filter_by(post_id=post.id,user_id=current_user.id).first()

        if post:
            return render_template(
                "item.html",
                title="Item",
                tab="item",
                post=post,
                hide=hide,
                vote=vote,
                fave=fave
            )
            
    return abort(404)

@post.route("/submit", methods=["GET", "POST"])
def submit():
    form = PostForm()
    args = request.args
    addr = request.remote_addr
    addr = str(addr) if addr else None
    group = None
    if "n" in args:
        group = args["n"].strip()
        try:
            group = int(group)
        except Exception as err:
            group = None
            
    if current_user.is_authenticated:
        user = current_user
    else:
        user = User.query.get(1)
        
    if form.validate_on_submit():
        if user.can_post():
            title = form.title.data.strip()
            url = form.url.data.strip()
            url_base = get_url_base(url)
            text = form.text.data
            
            post = Post(
                title=title,
                url=url,
                ip_address=addr,
                url_base=url_base,
                body="",
                author=user,
                parent_id=0,
                main_parent_id=0,
                path="/",
                group_id = group if group else 0
            )
            
            db.session.add(post)
            db.session.commit()
            
            user.karma = user.karma + 1
            
            vote = Vote(state=1, post_id=post.id, user_id=user.id, flag=1)
            db.session.add(vote)
                
            if text:
                reply = Post(title=f"Re: {title}",
                            body=text,
                            ip_address=addr,
                            parent_id=post.id,
                            main_parent_id=post.id,
                            user_id=user.id,
                            group_id=0,
                            path=f"{post.path}{post.id}/"
                        )
                db.session.add(reply)
                db.session.commit()
                
                vote = Vote(state=1,ip_address=addr, post_id=reply.id, user_id=user.id, flag=1)
                db.session.add(vote)
                db.session.commit()
            else:
                db.session.commit()
                
            flash("Congratulations, your post was submitted!","success")
            return redirect(url_for("post.item", id=post.id))
        
    elif "t" in args:
        t = args["t"]
        if form.title.data == None or form.title.data == "":
            if t == "a":
                form.title.data = "Ask NT: "
            elif t == "s":
                form.title.data = "Show NT: "
            elif t == "p":
                form.title.data = "Politics: "
            elif t == "n":
                form.title.data = "News: "
            elif t == "t":
                form.title.data = "Tech: "
            elif t == "e":
                form.title.data = "Event: "
            elif t == "j":
                form.title.data = "Job: "
            
    return render_template(
        "submit.html", 
        title="Submit",
        _pagename="Submit",
        tab="submit", 
        form=form
    )


@post.route('/reply',methods=['POST'])
def reply():
    error = jsonify({"error": "An error occured while commenting, please try reloading","text":"","main":True})
    form = request.form
    addr = request.remote_addr
    addr = str(addr) if addr else None
    
    if current_user.is_authenticated:
        user = current_user
    else:
        user = User.query.get(1)
    
    if "parent" in form and "text" in form and "tok" in form:
        parent = form["parent"]
        text = form["text"].strip()
        tok = form["tok"].strip()
        goto = form["goto"] if "goto" in form else  None
        try:
            post_id = int(parent)
        except Exception as err:
            return error
        
        post = Post.query.get(post_id)
        decoded_text = custom_decode(tok)
        passed = False
        
        if decoded_text:
            if type(decoded_text) == str:
                decoded_text = [x.strip() for x in decoded_text.split(":")]
                if len(decoded_text) == 3:
                    tok_username,tok_user_id,tok_post_id = decoded_text
                    try:
                        tok_user_id = int(tok_user_id)
                        tok_post_id = int(tok_post_id)
                    except Exception as err:
                        return error
                    
                    # print(decoded_text)
                    
                    if tok_username == user.username and \
                        tok_user_id == user.id and \
                        tok_post_id == post.id:
                            passed = True
                    
        if text and passed:
            if post:
                title = post.title
                if not title.lower().startswith("re:"):
                    title = f"Re: {title}"

                main_parent_id = post.main_parent_id 
                if main_parent_id == 0:
                    main_parent_id = post.id
                post = Post(title=title,
                            body=text,
                            ip_address=addr,
                            parent_id=post_id,
                            main_parent_id=main_parent_id,
                            user_id=user.id,
                            group_id=0,
                            path=f"{post.path}{post.id}/")

                # adding post to database
                db.session.add(post)
                db.session.commit()
                
                user.karma = user.karma + 1
            
                vote = Vote(state=1, ip_address=addr,post_id=post.id, user_id=user.id, flag=1)
                db.session.add(vote)
                db.session.commit()
                
                return jsonify({
                    "error": "",
                    "text":render_template("ind_comment.html",post=post,parent=None,ind=True),
                    "main":post_id == main_parent_id
                })
                    
    return error


@post.route('/vote',methods=['POST'])
def vote():
    error = jsonify({"error": "An error occured while voting, please try reloading"})
    addr = request.remote_addr
    addr = str(addr) if addr else None
    if current_user.is_authenticated:
        args = request.args
        #print(args)
        if "id" in args:
            state = args["state"] if "state" in args else "un"
            try:
                post_id = int(args["id"])
            except Exception as err:
                return error
            post = Post.query.get(post_id)
            vote = Vote.query.filter_by(post_id=post_id,user_id=current_user.id).first()
            if post.author !=  current_user:
                if vote:
                    post.author.karma = post.author.karma - 1
                    db.session.delete(vote)
                else:
                    if post:
                        post.author.karma = post.author.karma + 1
                        vote = Vote(state=1, ip_address=addr,post_id=post.id, user_id=current_user.id)
                        db.session.add(vote)
                    else:
                        return error
                db.session.commit()
            else:
                return jsonify({"error": "You can't unvote your post."})
            
            return jsonify({"error": ""})
            
    else:
        return jsonify({"error": "Login to vote a post"})
    return error


@post.route('/hide',methods=['POST'])
def hide():
    error = jsonify({"error": "An error occured while hiding post, please try reloading"})
    if current_user.is_authenticated:
        args = request.args
        if "id" in args:
            try:
                post_id = int(args["id"])
            except Exception as err:
                return error
            
            post = Post.query.get(post_id)
            hide = Hide.query.filter_by(post_id=post_id,user_id=current_user.id).first()
            
            if post.author !=  current_user:
                if hide:
                    db.session.delete(hide)
                else:
                    if post:
                        hide = Hide(post_id=post.id, user_id=current_user.id)
                        db.session.add(hide)
                    else:
                        return error
                db.session.commit()
                return jsonify({"error": ""})
    return jsonify({"error": "Login to hide a post"})


@post.route('/fave',methods=['POST'])
def fave():
    error = jsonify({"error": "An error occured while adding post to favourite, please try reloading"})
    if current_user.is_authenticated:
        args = request.args
        if "id" in args:
            try:
                post_id = int(args["id"])
            except Exception as err:
                return error

            post = Post.query.get(post_id)            
            fave = Favourite.query.filter_by(post_id=post_id,user_id=current_user.id).first()
            
            if fave:
                post.author.karma = post.author.karma - 1
                db.session.delete(fave)
            else:
                if post:
                    post.author.karma = post.author.karma + 1
                    fave = Favourite(post_id=post.id, user_id=current_user.id)
                    db.session.add(fave)
                else:
                    return error
            db.session.commit()
            return jsonify({"error": ""})
    return jsonify({"error": "Login to Favorite a post"})


@post.route('/delete',methods=['POST'])
def delete():
    error = jsonify({"error": "An error occured while deleting post, please try reloading"})
    if current_user.is_authenticated:
        args = request.args
        if "id" in args:
            try:
                post_id = int(args["id"])
            except Exception as err:
                return error
            post = Post.query.get(post_id)
            if current_user == post.author:
                if post:
                    if post.deleted == 1:
                        post.author.karma = post.author.karma + 1
                        post.deleted = 0
                    else:
                        post.author.karma = post.author.karma - 1
                        post.deleted = 1
                    db.session.commit()
                    return jsonify({"error": ""})
                
            elif current_user.is_admin():
                if post:
                    if post.deleted == 2:
                        post.author.karma = post.author.karma + 2
                        post.deleted = 0
                    else:
                        post.author.karma = post.author.karma - 2
                        post.deleted = 2
                    db.session.commit()
                    return jsonify({"error": ""})
                
            return error
    return jsonify({"error": "Login to delete a post"})


@post.route('/flag',methods=['POST'])
def flag():
    error = jsonify({"error": "An error occured while flagging post, please try reloading"})
    if current_user.is_authenticated:
        args = request.args
        if "id" in args:
            try:
                post_id = int(args["id"])
            except Exception as err:
                return error

            post = Post.query.get(post_id)            
            flag = Flag.query.filter_by(post_id=post_id,user_id=current_user.id).first()
            
            if flag:
                if len(post.flags) == 1:
                    post.flagged = 0
                db.session.delete(flag)
            else:
                if post:
                    flag = Flag(post_id=post.id, user_id=current_user.id)
                    post.flagged = 1
                    db.session.add(flag)
                else:
                    return error
            db.session.commit()
            return jsonify({"error": ""})
    return jsonify({"error": "Login to Flag a post"})

