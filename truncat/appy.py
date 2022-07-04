import sqlite3, string, secrets, bcrypt, os
from flask import Flask, redirect, render_template, session, g, flash, request
from forms import ContactForm, LoginForm, SignupForm, TruncateForm, LinkListForm

app = Flask(__name__)
app.secret_key = "abrvalg"

DATABASE = "truncat.sqlite"
PAGELIST = {
    "statist",
    "edit",
    "contact",
    "singup",
    "login",
    "logout",
    "linklist",
    "truncate",
    "index",
}


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
    """Получаем список ссылок пользователя в интервале от a до b"""
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


def get_the_one(id):
    """Получаем один элемент из БД по его сокращенному псевдониму"""
    db_item = (
        db()
        .execute(
            "SELECT input, ID as truncat FROM source INNER JOIN alias ON alias.url = source.truncat WHERE alias.ID=? ",
            (id,),
        )
        .fetchone()
    )
    if not db_item:
        db_item = (
            db()
            .execute("SELECT input, truncat FROM source where truncat = ?", (id,))
            .fetchone()
        )
    return db_item


def get_the_count():
    """Считаем количество страниц списка ссылок пользователя (по 5 шт на страницу)"""
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
    if db_items["count"] % 5 == 0:
        num_of_page = db_items["count"] // 5
    else:
        num_of_page = db_items["count"] // 5 + 1
    return num_of_page


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


@app.route("/statist", endpoint="statist", methods=["GET", "POST"])
def statistpage():
    """Отображение страницы статистики использования ссылки"""
    form = LinkListForm()
    # читаем из БД сокращенную сслыку и полную ссылку get_url["truncat"] и get_url["input"]
    get_url = get_the_one(request.args["id"])
    # читаем из БД лог переходов по данной сокращенной ссылке
    get_stat = (
        db()
        .execute("SELECT use_at, who, IP FROM log where what=?", (request.args["id"],))
        .fetchall()
    )
    count = len(get_stat)
    return render_template(
        "statist.html",
        form=form,
        urls=get_url,
        stat=get_stat,
        count=count,
    )


@app.route("/edit", endpoint="edit", methods=["POST", "GET"])
def editpage():
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
                # проверяем нахождение в списке марштуров
                a = form.output.data in PAGELIST
                if not in_db_truncat_table and not in_db_alias_table and not a:
                    # добавить вариант имени в БД
                    db().execute(
                        "INSERT INTO alias (ID, url, owner) VALUES (? , ?, ?)",
                        (form.output.data, g.out_url, g.logname),
                    )
                    db().commit()
                    flash("Новая сокращенная ссылка добавлена в базу данных")
                    return redirect("/linklist/1")
                flash("Такая короткая ссылка уже есть в нашей базе")
                flash("Выберите другое сокращение")
                return render_template(
                    "/edit.html",
                    form=form,
                )
            if temp == "redirect":
                return redirect(request.form["source"])
            if temp == "copy":
                copy_to_clipboard(g.origin + str(form.output.data))
                g.out_url = form.output.data
                return render_template(
                    "/edit.html",
                    form=form,
                )
        # прокинуть данные с предыдущей страницы
        if request.args["id"] != "0":
            get_log = get_the_one(request.args["id"])
            form.source.data = get_log["input"]
            form.output.data = get_log["truncat"]
        elif g.in_url:
            form.source.data = g.in_url
            form.output.data = g.out_url
        return render_template("edit.html", form=form, id=g.out_url)
    flash("Для получения списка своих ссылок вам необходимо войти в свой профиль")
    return redirect("/login")


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
    if g.logged:
        flash("Вы уже вошли в профиль под именем '" + g.logname + "'")
        return redirect("/")
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
        # определяем IP пользователя
        ip_addr = request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr)
        # пишем лог использования ссылки в БД
        db().execute(
            "INSERT INTO log (what, who, IP) VALUES (? , ?, ?)",
            (
                urlid,
                g.logname,
                ip_addr,
            ),
        )
        db().commit()
        return redirect(target_url["input"])
    # короткая ссылка отсуствует в БД
    if not urlid in PAGELIST:
        flash("Такая ссылка не найдена")
    return redirect("/")


@app.route("/linklist/<page>", methods=["GET", "POST"], endpoint="linklist")
def linklistpage(page):
    """Отображение ссылок пользователя"""
    page = int(page)
    form = LinkListForm()
    offset = (int(page) - 1) * 5
    count_of_list = get_the_count()
    # получаем начало и конец диапазона отображения цифр пагинатора
    if count_of_list > 3:
        if page - 1 < 1:
            stp = 1
            endp = stp + 2
        elif page + 1 > count_of_list:
            endp = count_of_list
            stp = endp - 2
        else:
            stp = page - 1
            endp = page + 1
    else:
        stp = 1
        endp = count_of_list

    if "copy" in set(request.form.keys()):
        copy_to_clipboard(g.origin + request.form["copy"])
        flash("Ссылка скопирована в буфер обмена")
        return render_template(
            "linklist.html",
            page=page,
            form=form,
            link_list=get_the_list(5, offset),
            count_of_list=count_of_list,
            offset=offset,
            stp=stp,
            endp=endp,
        )
    if "redirect" in set(request.form.keys()):
        return redirect(g.origin + request.form["redirect"])

    return render_template(
        "linklist.html",
        page=page,
        form=form,
        link_list=get_the_list(5, offset),
        count_of_list=count_of_list,
        offset=offset,
        stp=stp,
        endp=endp,
    )


@app.route("/truncate", endpoint="truncate", methods=["GET", "POST"])
def truncatepage():
    """Сокращаем ссылку, сохраняем в БД"""
    form = TruncateForm()
    my_location = request.url_root

    if form.validate_on_submit():
        temp = request.form["btm"]
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
                session["out_url"] = form.output.data
                session["in_url"] = form.source.data
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
            session["out_url"] = form.output.data
            session["in_url"] = form.source.data
            flash("Короткая ссылка готова")
    return render_template("truncate.html", form=form)


# главная функция
if __name__ == "__main__":
    app.run()
