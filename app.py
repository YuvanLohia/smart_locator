from flask import Flask,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
db = SQLAlchemy(app)
class Books(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    bookname = db.Column(db.String(100),nullable = False)
    shelf = db.Column(db.Integer,primary_key=True)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)