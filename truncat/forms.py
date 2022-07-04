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


class TruncateForm(FlaskForm):
    """Форма ввода ссылки для сокращения"""

    source = StringField(
        "url",
        validators=[
            validators.DataRequired(),
            validators.URL(require_tld=False),
        ],
        render_kw={
            "placeholder": "Введите ссылку для сокращения *",
            "class": "form-control",
        },
    )

    output = StringField(
        "output",
        render_kw={
            "placeholder": "Тут будет результат *",
            "class": "form-control",
            "readonly": "true",
        },
    )


class LinkListForm(FlaskForm):
    """Форма редактирования ссылки пользователя на странице со спи ском его ссылок"""

    source = StringField(
        "url",
        validators=[
            validators.DataRequired(),
            validators.URL(require_tld=False),
        ],
        render_kw={
            "class": "form-control",
            "readonly": "true",
        },
    )

    output = StringField(
        "output",
        render_kw={
            "class": "form-control",
            "aria-describedby": "basic-addon3",
        },
    )
