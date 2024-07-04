# imports
import time
from datetime import date
from flask import Flask, render_template, url_for, redirect, flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, IntegerField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
import threading
from gpiozero import LED
# flask settings
app = Flask(__name__)
app.config["SECRET_KEY"] = '5041f57bc44a6d1fe8bac351bdd7aaa5'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////home/yuvan/smart_locate/smart_locate/main.db"
db = SQLAlchemy(app)
bcrypt = Bcrypt()
login_manager = LoginManager(app)
login_manager.login_view = '/'
login_manager.login_message_category = "info"
type = "book"
searched = False
searched_items = []
shelf1 = LED(22)
shelf2 = LED(23)
shelf3 = LED(24)
# forms


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class SearchForm(FlaskForm):
    objectname = StringField(f"{type.title()} name",
                             validators=[DataRequired()])
    submit = SubmitField("Search")


class Comment(FlaskForm):
    comment_title = StringField("Comment Title", validators=[DataRequired()])
    comment_message = TextAreaField(
        "Comment Message", validators=[DataRequired()])

    submit = SubmitField("Comment")


class Register(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


class add_book(FlaskForm):
    bname = StringField(f"{type} Name:", validators=[DataRequired()])
    author = StringField("Author :", validators=[DataRequired()])
    description = TextAreaField("Desciption :", validators=[DataRequired()])
    shelf_no = IntegerField("Shelf No :", validators=[DataRequired()])
    submit = SubmitField(f"Add new {type}")
# models


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    objects = db.relationship('Object', backref='taken_user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}','{self.id}')"


class Object(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String, unique=True, nullable=False)
    shelf = db.Column(db.Float, nullable=False)
    taken = db.Column(db.Boolean, default=False)
    taken_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    author = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"User('{self.uname}')"


class Comments(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    Comment_message = db.Column(db.VARCHAR, nullable=False)
    Comment_title = db.Column(db.VARCHAR, nullable=False)
    Book_id = db.Column(db.Integer, db.ForeignKey('object.id'), nullable=False)
    User_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    Date = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Comment ('{self.Comment_message}')"

# functions


def light_on(shelf):
    print(shelf)
    if shelf == 1:
        shelf1.on()
    elif shelf == 2:
        shelf2.on()
    elif shelf == 3:
        shelf3.on()
    time.sleep(30)
    shelf1.off()
    shelf2.off()
    shelf3.off()
    print("done")
# routes


@app.route("/", methods=["GET", "POST"])
def index():
    if not current_user.is_authenticated:
        login = LoginForm()
        if login.validate_on_submit():
            user = User.query.filter_by(username=login.username.data).first()
            if user and bcrypt.check_password_hash(user.password, login.password.data):
                login_user(user, remember=False)

                return redirect(url_for("home"))
            else:
                flash("Incorrect username or password", "danger")
        return render_template('login.html', form=login)
    else:
        return redirect('home')


@app.route("/home", methods=["GET", "POST"])
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
            flash("Sorry no book found", "danger")
        else:
            searched = True
            return redirect("result")
    return render_template('index.html', title="Home Page", type=type, form=searchform, current_user=current_user)


@app.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect('/')


@app.route("/result")
@login_required
def result():
    global searched_items, searched
    if searched:
        searched = False
        sitem = searched_items
        searched_items = []
        return render_template("result.html", title="Result", type=type, result=sitem)
    else:
        return redirect("home")


@app.route("/detail/<object_id>")
@login_required
def detail(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    com = Comments.query.all()
    taken_name = ""
    if obj.taken:
        taken_name = User.query.filter_by(id=obj.taken_id).first().username

    coms = {}
    for v, i in enumerate(com):
        if i.Book_id == obj.id:
            delete_able = False
            if current_user.id == i.User_id or current_user.username == "admin":
                delete_able = True
            coms[str(v)] = [User.query.filter_by(
                id=i.User_id).first().username, i, delete_able]

    return render_template("detail.html", object=obj, title=obj.uname, type=type, comment=coms, taken_name=taken_name)


@app.route("/search/<object_id>")
@login_required
def search(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    thread = threading.Thread(target=light_on, args=(obj.shelf,))
    thread.start()
    com = Comments.query.all()
    coms = {}
    for v, i in enumerate(com):
        if i.Book_id == obj.id:
            deleUserte_able = False
            if current_user.id == i.User_id or current_user.name == "admin":
                delete_able = True
            coms[str(v)] = [User.query.filter_by(
                id=i.User_id).first().username, i, delete_able]
    flash("Light is now active over the shelf. It will remain active for 30 sec", "success")
    return render_template("detail.html", object=obj, title=obj.uname, type=type, comment=coms)


@app.route("/myobjects")
@login_required
def myobjects():
    object_list = current_user.objects

    return render_template("myobjects.html", title=f"My {type}", type=type, objlist=object_list)


@app.route("/take/<object_id>")
@login_required
def take(object_id):
    obj = Object.query.filter_by(id=object_id).first()
    obj.taken = True
    obj.taken_id = current_user.id
    db.session.commit()
    flash(f"{type} taken successfully", "success")
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


@app.route("/comment/<object_id>", methods=["GET", "POST"])
@login_required
def comment(object_id):
    searchform = Comment()
    if searchform.validate_on_submit():
        comment = Comments(Comment_message=searchform.comment_message.data, Comment_title=searchform.comment_title.data,
                           Book_id=object_id, User_id=current_user.id, Date=date.today())
        print(comment)
        db.session.add(comment)
        db.session.commit()
        return redirect(f"/detail/{object_id}")
    return render_template('comment.html', title="Add a comment", type=type, form=searchform)


@app.route("/lisbooks")
@login_required
def lisbooks():
    if current_user.username != "admin":
        return redirect("/")
    else:
        return render_template("result.html", title="List of Books", type=type, result=Object.query.all())


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if current_user.username != "admin":
        return redirect("/")
    else:
        form = Register()
        if form.validate_on_submit():
            nam = form.username.data
            if len(User.query.filter_by(username=nam).all()) != 0:
                flash("User with that username already exists", "danger")
            else:
                password = form.password.data

                password = Bcrypt().generate_password_hash(password)
                user = User(username=nam, password=password)
                db.session.add(user)
                db.session.commit()
                flash("User created", "info")
                return redirect("/lisuser")
        return render_template("register.html", title="Register", type=type, form=form)


@app.route("/addbook", methods=["GET", "POST"])
@login_required
def add_user():
    if current_user.username != "admin":
        return redirect("/")
    else:
        form = add_book()
        if form.validate_on_submit():
            nam = form.bname.data
            if len(Object.query.filter_by(uname=nam).all()) != 0:
                flash(f"{type} with that name already exists", "danger")
            else:
                author = form.author.data
                des = form.description.data
                shelf = form.shelf_no.data

                book = Object(uname=nam, shelf=shelf,
                              author=author, description=des)
                db.session.add(book)
                db.session.commit()
                flash(f"{type} Added", "info")
                return redirect("/lisbooks")
        return render_template("book_add.html", title="Add book", type=type, form=form)


@app.route("/delete/<comment_id>")
@login_required
def dele(comment_id):

    b = Comments.query.filter_by(id=comment_id).first().Book_id
    Comments.query.filter_by(id=comment_id).delete()
    db.session.commit()
    flash("Comment Deleted", "danger")
    return redirect(f"/detail/{b}")


@app.route("/lisuser")
@login_required
def lisuser():
    if current_user.username != "admin":
        return redirect("/")
    else:
        return render_template("userr.html", title="List of Users", type=type, result=User.query.all())


@app.route("/deleteuser/<user_id>")
@login_required
def deleuser(user_id):
    if current_user.username != "admin":
        return redirect("/")
    else:
        User.query.filter_by(id=user_id).delete()
        comments = Comments.query.filter_by(User_id=user_id).delete()

        db.session.commit()
        flash("User Deleted", "danger")
        return redirect(f"/lisuser")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
