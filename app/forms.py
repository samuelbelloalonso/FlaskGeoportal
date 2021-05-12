from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[
                           DataRequired()], render_kw={"placeholder": "Username"})

    password = PasswordField("Password", validators=[DataRequired()], render_kw={
                             "placeholder": "Password"})
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")], render_kw={
            "placeholder": "Repeat your password"}
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use a different username.")
