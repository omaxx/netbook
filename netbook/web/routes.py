from flask import current_app as app, render_template, flash, redirect
from flask_login import current_user, login_user, logout_user, login_required

from netbook import db
from . import forms


@app.route("/")
@login_required
def home():
    return render_template("home.html", title="Home page")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect("/")
    form = forms.Login()
    if form.validate_on_submit():
        try:
            user = db.User.get(name=form.username.data)
        except db.errors.DoesNotExist:
            user = None
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect("/login")
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")
