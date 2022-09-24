#imports
import time


from flask import Flask,render_template,url_for,redirect,flash
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,current_user,logout_user,login_required
import threading
#flask settings
app = Flask(__name__)
app.config["SECRET_KEY"] = '5041f57bc44a6d1fe8bac351bdd7aaa5'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///main.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view= '/'
login_manager.login_message_category = "info"
type = "book"
searched = False
searched_items = []
#forms
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Log in")
class SearchForm(FlaskForm):
    objectname = StringField(f"{type} name",validators=[DataRequired()])
    submit = SubmitField("Search")
#models
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    username = db.Column(db.String,unique=True,nullable=False)
    password = db.Column(db.String(60),nullable=False)
    objects = db.relationship('Object',backref = 'taken_user',lazy=True)
    def __repr__(self):
        return f"User('{self.username}','{self.id}')"
class Object(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key = True)
    uname = db.Column(db.String,unique=True,nullable=False)
    shelf = db.Column(db.Float,nullable=False)
    taken = db.Column(db.Boolean,default = False)
    taken_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable = True)
    def __repr__(self):
        return f"User('{self.uname}')"
#functions
def light_on(shelf):
    print(shelf)
    time.sleep(30)
    print("done")
#routes
@app.route("/",methods=["GET","POST"])
def index():
    if not current_user.is_authenticated:
        login = LoginForm()
        if login.validate_on_submit():
            user = User.query.filter_by(username=login.username.data).first()
            if user and bcrypt.check_password_hash(user.password,login.password.data) :
                login_user(user,remember=False)

                return redirect(url_for("home"))
            else:
                flash("Incorrect username or password", "danger")
        return render_template('login.html',form = login)
    else:
        return redirect('home')
@app.route("/home",methods=["GET","POST"])
@login_required
def home():
    global searched
    searched = False
    searchform = SearchForm()
    if searchform.validate_on_submit():
        objects = Object.query.all()
        for obj in objects:
            if str.lower(searchform.objectname.data) in obj.uname.lower():
                searched_items.append(obj)
        if len(searched_items) == 0:
            flash("Sorry no book found","danger")
        else:
            searched= True
            return  redirect("result")
    return render_template('index.html',title = "Home Page",type = type,form=searchform)

@app.route('/logout')
@login_required
def logout():

        logout_user()
        return redirect('/')
@app.route("/result")
@login_required
def result():
    global searched_items,searched
    if searched:
        searched = False
        sitem = searched_items
        searched_items = []
        return render_template("result.html",title="Result",type = type,result=sitem)
    else:
        return redirect("home")
@app.route("/detail/<object_id>")
@login_required
def detail(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    return render_template("detail.html",object = obj,title = obj.uname,type=type)
@app.route("/search/<object_id>")
@login_required
def search(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    thread = threading.Thread(target = light_on,args=(obj.shelf,))
    thread.start()
    flash("Light is now active over the shelf. It will remain active for 30 sec","success")
    return render_template("detail.html",object = obj,title = obj.uname,type=type)
@app.route("/myobjects")
@login_required
def myobjects():
    object_list = current_user.objects

    return render_template("myobjects.html",title =f"My {type}",type=type,objlist = object_list)
@app.route("/take/<object_id>")
@login_required
def take(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    obj.taken = True
    obj.taken_id = current_user.id
    db.session.commit()
    flash(f"{type} taken successfully","success")
    return redirect("/myobjects")
@app.route("/return/<object_id>")
@login_required
def return_o(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    obj.taken = False
    obj.taken_id = None
    db.session.commit()
    thread = threading.Thread(target=light_on, args=(obj.shelf,))
    thread.start()
    thread = threading.Thread(target=light_on, args=(obj.shelf,))
    thread.start()
    flash(f"{type} returned successfully, kindly keep {type} back in the shelf where the light is on", "success")
    return redirect("/myobjects")

if __name__ == "__main__":
    app.run(debug = True)