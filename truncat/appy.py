import sqlite3, string, secrets, bcrypt, os
from flask import Flask, redirect, render_template, session, g, flash, request
from forms import ContactForm, LoginForm, SignupForm, TruncateForm

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
        g.logged = False
        g.logname = "John Doe"


def db():
    """Подключение к базе данных (БД)"""
    if not hasattr(g, "db"):
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


def sulr():
    """Генератор уникальной ссылки"""
    alphabet = string.ascii_letters + string.digits
    truncate = "".join(secrets.choice(alphabet) for i in range(6))
    return truncate


@app.route("/")
def frontpage():
    """Отображение главной страницы"""
    return render_template("index.html")


@app.route("/about")
def aboutpage():
    return "Ok"


@app.route("/contact", endpoint="contact", methods=["GET", "POST"])
def contactpage():
    """Отправка сообщения администрации сайта"""
    form = ContactForm()
    if form.validate_on_submit():
        db().execute(
            "INSERT INTO message (name, email, content) VALUES (? , ?, ?)",
            (form.name.data, form.email.data, form.message.data),
        )
        db().commit()
        flash("Ваше сообщение успешно отправлено")
        return redirect("/")
    return render_template("contact.html", form=form)


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
            # выводим сообщение для пользователя
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
                flash("Вы вошли в свой профиль")
                return redirect("/truncate")
            flash("Введен неправильный пароль")
        else:
            flash("Пользователь с таким именем не найден")
    return render_template("login.html", form=form)


@app.route("/logout", endpoint="logout")
def logoutpage():
    """Обеспечение выхода пользователя из авторизированной зоны"""
    session.pop("logged_in", None)
    session.pop("log_name", None)
    flash("Вы покинули авторизированную зону. До новых встреч!")
    return redirect("/")


@app.route("/<urlid>", methods=["GET", "POST"], endpoint="redirection")
def redirectpage(urlid):
    """Перенаправление при переходе на короткую ссылку"""

    if len(urlid) == 6:
        target_url = (
            db()
            .execute("SELECT input FROM source WHERE truncat=(?)", (urlid,))
            .fetchone()
        )
        if target_url:
            return redirect(target_url["input"])
    flash("Такая ссылка не найдена")
    return redirect("/")


@app.route("/linklist")
def linklistpage():
    pass


@app.route("/truncate", endpoint="truncate", methods=["GET", "POST"])
def truncatepage():
    """Сокращаем ссылку, сохраняем в БД"""
    form = TruncateForm()
    my_location = request.origin

    if form.validate_on_submit():
        temp = request.form["btm"]
        # копирование в буфер обмена
        if temp == "copy":
            command = "echo " + str(form.output.data).strip() + "| clip"
            os.system(command)
            flash("Короткая ссылка скопирована в буфер обмена")

        # перенаправление на целевую страницу
        if temp == "redirect":
            return redirect(request.form["source"])
        db_obj = (
            db()
            .execute("SELECT truncat FROM source WHERE input=(?)", (form.source.data,))
            .fetchone()
        )
        if temp == "submit":
            # проверяем наличие ссылки в БД
            if db_obj:
                form.output.data = my_location + "/" + db_obj["truncat"]
                flash("Короткая ссылка уже есть в нашей базе")
                flash("Вы можете ее использовать")
                return render_template("truncate.html", form=form)
            # проверяем на совпадение с уже существующими в БД новой короткой ссылки
            while True:
                truncat = sulr()
                db_surl = (
                    db()
                    .execute("SELECT truncat FROM source WHERE input=(?)", (truncat,))
                    .fetchone()
                )
                if db_surl != truncat:
                    break
            # добавляем в БД новую ссылку
            if g.logged:
                db().execute(
                    "INSERT INTO source (truncat, input, owner) VALUES (? , ?, ?)",
                    (truncat, form.source.data, g.logname),
                )
            else:
                db().execute(
                    "INSERT INTO source (truncat, input) VALUES (? , ?)",
                    (truncat, form.source.data),
                )
            db().commit()
            form.output.data = my_location + "/" + truncat
            flash("Короткая ссылка готова")
    return render_template("truncate.html", form=form)


# главная функция
if __name__ == "__main__":
    app.run()
