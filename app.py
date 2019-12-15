"""
docstring
"""
from flask import Flask, render_template, request, g, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
import requests
import itertools
import os
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators, TextAreaField
from wtforms.validators import Regexp, Required, ValidationError

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
email = None
password = None
results= None

def login_check(form, field):
    res = db.session.execute("select email from users")
    emails = res.fetchall()
    login_email = form.email.data
    for i in range(len(emails)):
        emails[i] = emails[i][0]
    if not login_email in emails or not login_email:
        raise ValidationError("Incorrect User Name or Password")
    
def pass_check(form, field):
    res = db.session.execute("select pass_word from users")
    passwords = res.fetchall()
    login_password = form.password.data
    for i in range(len(passwords)):
        passwords[i] = passwords[i][0]
    if not login_password in passwords or not login_password:
        raise ValidationError("Incorrect User Name or Password")

def reg_check(form, field):
    res = db.session.execute("select email from users")
    emails = res.fetchall()
    login_email = form.remail.data
    for i in range(len(emails)):
        emails[i] = emails[i][0]
    if login_email in emails or not login_email:
        raise ValidationError("Username taken or unusable")
    
class LoginForm(FlaskForm):
    email = StringField("User Name", validators=[login_check])
    password = StringField("Password", validators=[pass_check])
    submit = SubmitField("Login")

class NewPost(FlaskForm):
    building = SelectField("Building",  choices=[('17th', '17th'),
                                                 ('Territorial', 'Territorial'), ('Frontier', 'Frontier'),
                                                 ('Sanford', 'Sanford'), ('Centennial', 'Centennial'),
                                                 ('Comstock', 'Comstock'), ('Middlebrook', 'Middlebrook'),
                                                 ('Pioneer', 'Pioneer')],  validators =[validators.required()])
    title = StringField("Title", validators =[validators.required()])
    review = TextAreaField("Review", validators =[validators.required()])
    photo1 = StringField("Link to photo (optional)", validators=[validators.URL()])
    photo2 = StringField("Link to photo (optional)", validators=[validators.URL()])
    photo3 = StringField("Link to photo (optional)", validators=[validators.URL()])
    submit = SubmitField("Post")

class RegisterForm(FlaskForm):
    remail = StringField("User Name", validators=[reg_check])
    rpassword = StringField("Password")
    rsubmit = SubmitField("Register")

class SearchForm(FlaskForm):
    search = StringField("Search")
    submit = SubmitField("Go!")
    
csrf = CSRFProtect()
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    global email
    global password
    form = LoginForm()
    reg = RegisterForm()
    login_email = form.email.data
    login_password = form.password.data
    reg_email = reg.remail.data
    reg_password = reg.rpassword.data
    print(email)
    print(password)
    if form.validate_on_submit() and login_email and login_password or email:
        email = form.email.data
        password = form.password.data
        return redirect(url_for("search"))
    elif reg.validate_on_submit() and reg_email and reg_password or email:
        email = reg.remail.data
        password = reg.rpassword.data
        res = db.session.execute("select email from users")
        emails = res.fetchall()
        query = "INSERT INTO users VALUES ('{}', '{}');".format(email, password)
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for("search"))
    else: return render_template("login.html", form=form, reg=reg)


        
@app.route('/search', methods=['GET', 'POST'])
def search():
    print(email)
    print(password)
    form=SearchForm()
    return render_template("search.html", form=form)

@app.route('/postings_list', methods=['GET', 'POST'])
def postings_list():
    global email
    global password
    print(email)
    print(password)
    form=SearchForm()
    print(form.search.data)
    print(bool(form.validate_on_submit()))
    query = form.search.data
    res = db.session.execute("select * from posts join buildings on posts.building = buildings.name")
    posts = res.fetchall()
    print(posts)
    body=''
    results=[]
    for i in posts:
        if query.lower() in i[1].lower() or query.lower() in i[3].lower() or query.lower() in i[2].lower():
            upload_id = i[4]
            query = "select url from images where upload_id = {}".format(upload_id)
            res = db.session.execute(query)
            imgs = res.fetchall()
            print('Images {}'.format(imgs))
            for i in range(len(imgs)):
                imgs[i] = imgs[i][0]
            lat = i[6]
            lat = i[7]
            title = i[1]
            desc = i[2]
            body="https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels?pp="+lat+","+lon+";4;"+title
            body+="&key=AvWjYu-PKLX_yA_wjaiVhhgn8L4zISfT_zN1cpFjwLyzByKro4crRk6pOE1r8fmI"
            results.append((body, title, desc, imgs))
    return render_template("postings_list.html", search_res=results)


@app.route('/new_posting', methods=['GET', 'POST'])
def new_posting():
    global email
    global password
    print(email)
    print(password)
    form = NewPost()
    if form.title.data and form.review.data and form.building.data:
        query = "select id from posts order by desc limit 1"
        posts = db.session.execute(query)
        posts = res.fetchall()
        print(posts)
        ide = posts[0]+1

        if form.photo1.data:
            query = "INSERT INTO images values ('{}', '{}');".format(form.photo1.data, ide)
            db.session.execute(query)
            db.session.commit()
        if form.photo2.data:
            query = "INSERT INTO images values ('{}', '{}');".format(form.photo2.data, ide)
            db.session.execute(query)
            db.session.commit()
        if form.photo3.data:
            query = "INSERT INTO images values ('{}', '{}');".format(form.photo3.data, ide)
            db.session.execute(query)
            db.session.commit()

        query = "select building from buildings where name = {}".format(form.building.data)
        building = db.session.execute(query)
        building = res.fetchall()
        building[0]
        
        query = "INSERT INTO posts VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(email, form.title.data, form.review.data, building, ide, ide)
        res = db.session.execute("select * from posts join buildings on posts.building = buildings.name")
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for("search"))
    return render_template("new_post.html", form = form)

                
##@app.route('/search', methods=['GET', 'POST'])
##def search():
##    global results
##    global email
##    global password
##    form = LoginForm()
##    reg = RegisterForm()
##    login_email = form.email.data
##    login_password = form.password.data
##    reg_email = reg.remail.data
##    reg_password = reg.rpassword.data
##    print(email)
##    print(password)
##    if form.validate_on_submit() and login_email and login_password or email:
##        email = form.email.data
##        password = form.password.data
##    elif reg.validate_on_submit() and reg_email and reg_password or email:
##        email = reg.remail.data
##        password = reg.rpassword.data
##        res = db.session.execute("select email from users")
##        emails = res.fetchall()
##        query = "INSERT INTO users VALUES ('{}', '{}');".format(email, password)
##        db.session.execute(query)
##        db.session.commit()
##    else: return render_template("login.html", form=form, reg=reg)
