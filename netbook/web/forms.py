from flask_wtf import FlaskForm

import wtforms as wtf


class Login(FlaskForm):
    username = wtf.StringField("Username", validators=[wtf.validators.DataRequired()])
    password = wtf.PasswordField("Password", validators=[wtf.validators.DataRequired()])
    remember_me = wtf.BooleanField("Remember Me")
    submit = wtf.SubmitField("Sign In")
