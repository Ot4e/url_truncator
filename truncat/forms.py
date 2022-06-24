from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField


class LoginForm(FlaskForm):
    name = StringField(
        "name",
        validators=[validators.DataRequired()],
        render_kw={"placeholder": "Ваше имя *", "class": "form-control"},
    )
    password = PasswordField(
        "password",
        validators=[validators.DataRequired()],
        render_kw={"placeholder": "Ваш пароль *", "class": "form-control"},
    )
