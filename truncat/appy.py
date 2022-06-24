from flask import Flask, redirect, render_template, session, g
from forms import LoginForm

app = Flask(__name__)
app.secret_key = "secret"

DATABASE = "truncat.sqlite"


@app.before_request
def global_vars():
    if session.get("logged_in"):
        g.logged = True


@app.route("/")
def frontpage():
    return render_template("index.html")


@app.route("/about")
def aboutpage():
    return "Ok"


@app.route("/contact")
def contactpage():
    return "Ok"


@app.route("/signup")
def signuppage():
    pass


@app.route("/login", endpoint="login", methods=["GET", "POST"])
def loginpage():
    form = LoginForm()
    if form.validate_on_submit():
        # if form.name.data == logname and form.password.data == lognamepassw:
        session["logged_in"] = True
        return redirect("/truncate")
    return render_template("login.html", form=form)


@app.route("/logout", endpoint="logout")
def logoutpage():
    session.pop("logged_in", None)
    return redirect("/")


@app.route("/<urlid>", methods=["GET", "POST"], endpoint="redirect")
def redirectpage():
    pass


@app.route("/linklist")
def linklistpage():
    pass


@app.route("/truncate")
def truncatepage():
    pass


if __name__ == "__main__":
    app.run()
