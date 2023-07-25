from datetime import timedelta
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from fileinput import filename

app = Flask(__name__)
app.secret_key = "1234"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class users(db.Model):    # type: ignore
    username = db.Column(db.String(100), primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, username, email, password):
        self.email = email
        self.username = username
        self.password = password

class images(db.Model): # type: ignore
    name = db.Column(db.String(100), primary_key=True)
    image = db.Column(db.BLOB)

    def __init__(self, name, image):
        self.name = name
        self.image = image


@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        name = request.form["username"].capitalize()
        mail = request.form["email"].lower()
        password = sha256_crypt.encrypt(request.form["password"])

        found_user = users.query.filter_by(username = name).first()
        found_email = users.query.filter_by(email = mail).first()
        if found_user:
            flash("Username already taken")
            return render_template("signup.html")
        elif found_email:
            flash("Email alredy used in an account")
            return redirect(url_for('register'))
        else:
            usr = users(name, mail, password)
            db.session.add(usr)
            db.session.commit()

            flash("registration successful! login with credentials")
            return redirect(url_for("login"))
    else:
        return render_template("signup.html")

@app.route("/signin", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        try:
            session.permanent = True
            uname = request.form["username"].capitalize()
            password = request.form["password"]
            session["username"] = uname

            found_user = users.query.filter_by(username = uname).first()
            user_password = found_user.password

            if found_user and sha256_crypt.verify(password, user_password):
                
                session["password"] = found_user.password
                flash("login successful!")
                return redirect(url_for("user"))
            else:
                flash("Incorect username Password combination")
                return render_template("signin.html")
        except:
            flash("User not found")
            return render_template("signin.html")
    else:
        if "username" in session:
            flash("Already logged in")
            return redirect(url_for("user"))
        return render_template("signin.html")

@app.route("/user")
def user():
    Users = users.query.all()
    try:
        username = session["username"]
        
        return render_template("user.html", Users = Users, username = username)
    except:
        flash("You were logged out after 5 minutes of inactivity!")
        return redirect(url_for('login'))
        
@app.route("/upload", methods = ["POST", "GET"])
def upload():
    if request.method == "POST":
        image_name = request.form["name"]
        image = request.files["image"]
        try:
            image.save(image.filename)  # type: ignore
            return redirect(url_for("user"))
        except:
            return redirect(url_for("home"))
    else:
        flash("unsuccessful")
        return render_template("upload.html")

@app.route("/products")
def products():

    return render_template("products.html")

@app.route("/cart", methods=["POST", "GET"])
def cart():
    try:
        image_name = request.form["image"].capitalize()
        search = images.query.filter_by(name = image_name).first()
        name = search.name
        image = search.image
        location = "/home/psycho/Documents/Python/Flask/Apps/Basic/static/down-Images/"
        filename = location+name+".jpg"
        with open(filename, 'wb') as file:
            file.write(image)
        return render_template("cart.html")
    except:
        return render_template("query.html")


@app.route("/signout")
def logout():
    if "username" in session:
        username = session["username"]
        flash(f"You have been logged out, {username}","info")
    session.pop("username", None)
    session.pop("password", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.run(debug=True)