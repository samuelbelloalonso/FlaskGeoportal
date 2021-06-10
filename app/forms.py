from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Recordarme")
    submit = SubmitField("Autenticarse")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(message="Debe introducir un nombre de usuario")],
        render_kw={"placeholder": "Nombre de usuario"},
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(message="Debe introducir una contraseña")],
        render_kw={"placeholder": "Contraseña"},
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[
            DataRequired(message="Debe introducir una contraseña"),
            EqualTo("password", message="Las contraseñan deben coincidir"),
        ],
        render_kw={"placeholder": "Repita su contraseña"},
    )
    submit = SubmitField("Darse de alta")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Por favor use un nombre de usuario diferente.")
