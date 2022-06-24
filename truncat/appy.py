from flask import Flask, render_template

app = Flask(__name__)

DATABASE = "truncat.sqlite"


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
def sognuppage():
    pass


@app.route("/login")
def loginpage():
    pass


@app.route("/logout")
def logoutpage():
    pass


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
