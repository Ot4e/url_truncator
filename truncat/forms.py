"""Формы для сайта"""

from flask_wtf import FlaskForm
from wtforms import StringField, validators, PasswordField


class LoginForm(FlaskForm):
    """Форма входа для зарегистрированного пользователя"""

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


class SignupForm(FlaskForm):
    """Форма регистрации нового пользователя"""

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
    password2 = PasswordField(
        "password2",
        validators=[validators.DataRequired()],
        render_kw={"placeholder": "еще раз Ваш пароль *", "class": "form-control"},
    )
