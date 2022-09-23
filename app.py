from flask import Flask,render_template,url_for,redirect
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config["SECRET_KEY"] = '5041f57bc44a6d1fe8bac351bdd7aaa5'
books = [{
    'id' : 1,
    'book_name':"Feluda",
     'shelf':1.1,
     'taken':'noone'
},
{
    'id' : 2,
    'book_name':"Agatha Criste",
     'shelf':1.2,
     'taken': "Yuvan"
},
{
    'id' : 3,
    'book_name':"Hercule Piort",
     'shelf':2,
     'taken':'noone'
}
]
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Log in")
@app.route("/",methods=["GET","POST"])
def index():
        login = LoginForm()
        if login.validate_on_submit():

            return redirect(url_for("home"))
        return render_template('login.html',form = login)
@app.route("/home")
def home():
    return render_template('index.html',title = "Home Page",type = "book")
if __name__ == "__main__":
    app.run(debug=True)