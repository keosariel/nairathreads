from flask import (
    flash, 
    redirect, 
    render_template, 
    request, 
    url_for,
    current_app
)
from flask_login import (
    current_user, 
    login_user, 
    logout_user
)
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash

from app import db
from app.auth import auth
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
    ChangePasswordForm
)
from app.models import User
from app.auth.email import send_password_reset_email

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.home"))


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = LoginForm()
    if form.validate_on_submit():
        username = str(form.username.data).lower().strip()
        password = form.password.data
        #with current_app.app_context():
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Invalid username or password","error")
            return redirect(url_for("auth.login"))
        login_user(user, remember=True)
        next_page = request.args.get("next")
        goto = request.args.get("goto")
        next_page = goto if goto else next_page
        if not next_page:
            next_page = url_for("author.profile", username=user.username)
        return redirect(next_page)
    return render_template("auth/login.html", title="Sign In",pagename="login",tab="login", form=form)



@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        username = str(form.username.data).lower().strip()
        password = form.password.data
        #with current_app.app_context():
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!","success")
        next_page = request.args.get("next")
        goto = request.args.get("goto")
        next_page = goto if goto else next_page
        if not next_page:
            next_page = ""
        return redirect(url_for("auth.login",next=next_page))
    return render_template("auth/signup.html", title="Register",pagename="sign up",tab="register", form=form)


@auth.route('/changepw',methods=['GET','POST'])
def changepw():
    form = ChangePasswordForm(current_user)
    if form.validate_on_submit():
        password = form.new_password.data
        current_user.set_password(password)
        db.session.commit()
        flash("Your changes have been saved.","success")
        return redirect(url_for("author.profile", username=current_user.username))
        
    return render_template(
        "changepw.html", 
        title="Change Password", 
        pagename="Change password",
        tab="change password",
        form=form
    )
    
@auth.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("author.profile", username=current_user.username))
    
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("An email with instructions was sent to your address.","info")
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html", 
        title="Reset Password Request", 
        pagename="Reset password",
        tab="reset password request",
        form=form
    )

@auth.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    user = User.verify_reset_password_token(token)
    
    if not user:
        flash("Invalid reset token.","error")
        return redirect(url_for("auth.login"))
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.","success")
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password.html", 
        tab="reset password",
        pagename="Reset password",
        title="Reset password",
        form=form
    )