from flask import Flask

app = Flask(__name__)

DATABASE = "truncat.sqlite"


@app.route("/")
def frontpage():
    return "Ok"


if __name__ == "__main__":
    app.run()
