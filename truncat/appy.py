import sqlite3, string, secrets, bcrypt, os
from flask import Flask, redirect, render_template, session, g, flash, request
from forms import ContactForm, LoginForm, SignupForm, TruncateForm, LinkListForm

app = Flask(__name__)
app.secret_key = "abrvalg"

DATABASE = "truncat.sqlite"


@app.before_request
def global_vars():
    """Установка глобальных переменных для работы с залогиненным пользователем"""
    g.origin = request.url_root
    if session.get("in_url"):
        g.in_url = session.get("in_url")
        g.out_url = session.get("out_url")[len(g.origin) :]
    else:
        g.in_url = g.out_url = False
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


def get_the_list(a, b):
    db_items = (
        db()
        .execute(
            "SELECT input, truncat, ID, alias.make_at FROM source INNER JOIN alias ON alias.url = source.truncat WHERE alias.owner=(?) UNION SELECT input, truncat, truncat, make_at FROM source WHERE source.owner=(?) order by make_at DESC LIMIT (?) OFFSET (?)",
            (
                g.logname,
                g.logname,
                a,
                b,
            ),
        )
        .fetchall()
    )
    return db_items


def get_the_count():
    db_items = (
        db()
        .execute(
            "SELECT MAX(Rcount) + MAX(Acount) AS count FROM (SELECT COUNT(*) AS Rcount, 0 AS Acount FROM source INNER JOIN alias ON alias.url = source.truncat WHERE alias.owner=(?) UNION SELECT 0, COUNT(*) AS Acount FROM source WHERE source.owner=(?))",
            (
                g.logname,
                g.logname,
            ),
        )
        .fetchone()
    )
    return db_items["count"]


def sulr():
    """Генератор уникальной ссылки"""
    alphabet = string.ascii_letters + string.digits
    truncate = "".join(secrets.choice(alphabet) for i in range(6))
    return truncate


def copy_to_clipboard(url_str):
    """Копирование ссылки в оперативную память"""
    command = "echo " + str(url_str).strip() + "| clip"
    os.system(command)
    flash("Короткая ссылка скопирована в буфер обмена")


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
                return redirect("/linklist")
            flash("Введен неправильный пароль")
        else:
            flash("Пользователь с таким именем не найден")
    return render_template("login.html", form=form)


@app.route("/logout", endpoint="logout")
def logoutpage():
    """Обеспечение выхода пользователя из авторизированной зоны"""
    session.pop("logged_in", None)
    session.pop("log_name", None)
    session.pop("in_url", None)
    session.pop("out_url", None)
    flash("Вы покинули авторизированную зону. До новых встреч!")
    return redirect("/")


@app.route("/<urlid>", methods=["GET", "POST"], endpoint="redirection")
def redirectpage(urlid):
    """Перенаправление при переходе на короткую ссылку"""

    target_url = False
    # проверяем короткую ссылку как пользовательскую версию
    if len(urlid) != 6:
        target = db().execute("SELECT url FROM alias WHERE ID=(?)", (urlid,)).fetchone()
        if target:
            target_url = (
                db()
                .execute("SELECT input FROM source WHERE truncat=(?)", (target["url"],))
                .fetchone()
            )
    # ищем короткую ссылку в основном списке
    else:
        target_url = (
            db()
            .execute("SELECT input FROM source WHERE truncat=(?)", (urlid,))
            .fetchone()
        )
    # перенаправляем на целевую страницу
    if target_url:
        return redirect(target_url["input"])
    # короткая ссылка отсуствует в БД
    flash("Такая ссылка не найдена")
    return redirect("/")


@app.route("/linklist", methods=["GET", "POST"], endpoint="linklist")
def linklistpage():
    """Отображение ссылок пользователя"""
    # получаем количество ссылок для данного пользователя
    count_of_list = get_the_count()
    if count_of_list % 5 == 0:
        paginator = count_of_list // 5
    else:
        paginator = count_of_list // 5 + 1
    # получаем часть ссылок для отображения на странице
    link_list = get_the_list(5, 0)
    form = LinkListForm()
    if g.logged:
        if form.validate_on_submit():
            temp = request.form["btm"]
            if temp == "save":
                # проверить уникальность предлагаемого варианта
                in_db_truncat_table = (
                    db()
                    .execute(
                        "SELECT truncat FROM source WHERE truncat=(?)",
                        (form.output.data,),
                    )
                    .fetchone()
                )
                in_db_alias_table = (
                    db()
                    .execute("SELECT ID FROM alias WHERE ID=(?)", (form.output.data,))
                    .fetchone()
                )
                if not in_db_truncat_table and not in_db_alias_table:
                    # добавить вариант имени в БД
                    db().execute(
                        "INSERT INTO alias (ID, url, owner) VALUES (? , ?, ?)",
                        (form.output.data, g.out_url, g.logname),
                    )
                    db().commit()
                    flash("Новая сокращенная ссылка добавлена в базу данных")
                    g.out_url = form.output.data
                    session.pop("in_url", None)
                else:
                    flash("Такая короткая ссылка уже есть в нашей базе")
                    flash("Выберите другое сокращение")
                    return render_template(
                        "linklist.html",
                        form=form,
                        link_list=link_list,
                        count_of_list=paginator,
                    )
            if temp == "redirect":
                return redirect(request.form["source"])
            if temp == "copy":
                copy_to_clipboard(g.origin + str(form.output.data))
                g.out_url = form.output.data
                return render_template(
                    "/linklist.html",
                    form=form,
                    link_list=link_list,
                    count_of_list=paginator,
                )
        # прокинуть данные из формы /truncat
        if g.in_url:
            form.source.data = g.in_url
            form.output.data = g.out_url
            return render_template(
                "/linklist.html",
                form=form,
                link_list=link_list,
                count_of_list=paginator,
            )
        return render_template(
            "linklist.html",
            form=form,
            link_list=link_list,
            count_of_list=paginator,
        )
    flash("Для получения списка своих ссылок вам необходимо войти в свой профиль")
    return redirect("/login")


@app.route("/truncate", endpoint="truncate", methods=["GET", "POST"])
def truncatepage():
    """Сокращаем ссылку, сохраняем в БД"""
    form = TruncateForm()
    my_location = request.url_root

    if form.validate_on_submit():
        temp = request.form["btm"]
        # редактирование короткой ссылки для зареганых пользователей
        if temp == "edit":
            session["in_url"] = form.source.data
            session["out_url"] = form.output.data
            return redirect("/linklist")
        # копирование в буфер обмена
        if temp == "copy":
            copy_to_clipboard(str(form.output.data))
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
                form.output.data = my_location + db_obj["truncat"]
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
            form.output.data = my_location + truncat
            flash("Короткая ссылка готова")
    return render_template("truncate.html", form=form)


# главная функция
if __name__ == "__main__":
    app.run()
