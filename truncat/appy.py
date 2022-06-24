from crypt import methods
from flask import Flask

app = Flask(__name__)

DATABASE = "truncat.sqlite"


@app.route("/")
def frontpage():
    return "Ok"


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


@app.route("/<urlid>", method=["GET", "POST"], endpoint="redirect")
def redirectpage():
    pass


if __name__ == "__main__":
    app.run()
