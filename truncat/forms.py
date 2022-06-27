"""Формы для сайта"""

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    validators,
    PasswordField,
    TextAreaField,
    EmailField,
)


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


class ContactForm(FlaskForm):
    """Форма отправки сообщения"""

    name = StringField(
        "name",
        validators=[validators.DataRequired()],
        render_kw={"placeholder": "Ваше имя *", "class": "form-control"},
    )

    email = EmailField(
        "email",
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
        render_kw={"placeholder": "Ваш email *", "class": "form-control"},
    )

    message = TextAreaField(
        "phone",
        validators=[
            validators.DataRequired(),
        ],
        render_kw={
            "placeholder": "Ваше сообщение *",
            "class": "form-control",
        },
    )
