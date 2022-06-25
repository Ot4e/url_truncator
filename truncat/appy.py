import sqlite3
import bcrypt
from flask import Flask, redirect, render_template, session, g, flash
from forms import LoginForm, SignupForm

app = Flask(__name__)
app.secret_key = "abrvalg"

DATABASE = "truncat.sqlite"


@app.before_request
def global_vars():
    """Установка глобальных переменных для работы с залогиненным пользователем"""
    if session.get("logged_in"):
        g.logged = True
        g.logname = session.get("log_name")
    else:
        g.logname = "John Doe"


def db():
    """Подключение к базе данных (БД)"""
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.route("/")
def frontpage():
    """Отображение главной страницы"""
    return render_template("index.html")


@app.route("/about")
def aboutpage():
    return "Ok"


@app.route("/contact")
def contactpage():
    return "Ok"


@app.route("/signup", endpoint="singup", methods=["GET", "POST"])
def signuppage():
    """Отображение и обработка формы регистрации"""
    form = SignupForm()
    if form.validate_on_submit():
        registred_name = db().execute("SELECT login FROM users").fetchall()
        if form.password.data == form.password2.data:
            # проверка ниличия такого же имени в БД
            for i in registred_name:
                if form.name.data == i[0]:
                    flash("Это имя уже используется, выбирите другое")
                    return render_template("signup.html", form=form)
            # хэширование пароля для безопасного хранения в БД
            salt = bcrypt.gensalt()
            password = form.password.data.encode("utf-8")
            password_hash = bcrypt.hashpw(password, salt)
            # добавляем нового пользователя в БД
            db().execute(
                "INSERT INTO users (login, passw) VALUES (? , ?)",
                (form.name.data, password_hash),
            )
            db().commit()
            # где выводить это сообщение?
            flash("Вы успешно зарегистрированы и вошли в свой новый профиль")
            session["logged_in"] = True
            # имя залогиненного пользователя
            session["log_name"] = form.name.data
            return redirect("/")
        flash("Введенные пароли не совпадают, попробуйте еще раз")
    return render_template("signup.html", form=form)


@app.route("/login", endpoint="login", methods=["GET", "POST"])
def loginpage():
    """Вход зарегистрированного пользователя"""
    form = LoginForm()
    if form.validate_on_submit():
        db_passw = (
            db()
            .execute("SELECT passw FROM users WHERE login=(?)", (form.name.data,))
            .fetchone()
        )
        # сверка пароля из БД с введенным для данного пользователя
        if db_passw:
            log_passw = form.password.data.encode("utf-8")
            if bcrypt.checkpw(log_passw, db_passw["passw"]):
                session["log_name"] = form.name.data
                session["logged_in"] = True
                return redirect("/")
            flash("Введен неправильный пароль")
        else:
            flash("Пользователь с таким именем не найден")
    return render_template("login.html", form=form)


@app.route("/logout", endpoint="logout")
def logoutpage():
    """Обеспечение выхода пользователя из авторизированной зоны"""
    session.pop("logged_in", None)
    session.pop("log_name", None)
    return redirect("/")


@app.route("/<urlid>", methods=["GET", "POST"], endpoint="redirection")
def redirectpage():
    pass


@app.route("/linklist")
def linklistpage():
    pass


@app.route("/truncate")
def truncatepage():
    pass


# главная функция
if __name__ == "__main__":
    app.run()
