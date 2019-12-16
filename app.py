"""
docstring
"""
from flask import Flask, render_template, request, g, redirect, url_for, session
import flask
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

csrf = CSRFProtect()
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

def set_cookie(email):
    session['email'] = email
    return email
    
def get_email():
    username = session.get('email', None)
    return username
    
def login_check(form, field):
    res = db.session.execute("select * from users")
    emails = res.fetchall()
    login_email = form.email.data
    password = form.password.data
    if not (login_email, password) in emails or not login_email:
        raise ValidationError("Incorrect User Name or Password")

def len_check_rev(form, field):
    if len(form.review.data)>1000:
        raise ValidationError("Review too long! Max 1000 characters.")

def len_check_pic(form, field):
    if len(form.photo1.data)>200:
        raise ValidationError("Link too long! Max 200 characters.")
    if len(form.photo2.data)>200:
        raise ValidationError("Link too long! Max 200 characters.")
    if len(form.photo3.data)>200:
        raise ValidationError("Link too long! Max 200 characters.")

def len_check_log(form, field):
    if len(form.email.data)>45 or len(form.password.data)>45:
        raise ValidationError("Entry too long! Max 45 characters.")

def len_check_tit(form, field):
    if len(form.title.data)>45:
        raise ValidationError("Entry too long! Max 45 characters.")

def len_check_reg(form, field):
    if len(form.remail.data)>45 or len(form.rpassword.data)>45:
        raise ValidationError("Entry too long! Max 45 characters.")
    
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
    login_pass = form.remail.data
    for i in range(len(emails)):
        emails[i] = emails[i][0]
    if login_email in emails or (login_pass and not login_email) or (login_email and not login_pass):
        raise ValidationError("Registration failed. Username taken or field missing")
    
class LoginForm(FlaskForm):
    email = StringField("Username")
    password = StringField("Password", validators=[login_check, len_check_log])
    submit = SubmitField("Login")

class NewPost(FlaskForm):
    building = SelectField("Building",  choices=[('17th', '17th'),
                                                 ('Territorial', 'Territorial'), ('Frontier', 'Frontier'),
                                                 ('Sanford', 'Sanford'), ('Centennial', 'Centennial'),
                                                 ('Comstock', 'Comstock'), ('Middlebrook', 'Middlebrook'),
                                                 ('Pioneer', 'Pioneer'), ('Bailey', 'Bailey')],  validators =[validators.required()])
    title = StringField("Title", validators =[validators.Length(max=44), validators.required()])
    review = TextAreaField("Review", validators =[validators.required(), validators.Length(max=999)])
    photo1 = StringField("Link to photo (optional)", validators=[validators.Optional(), validators.URL(), validators.Length(max=199)])
    photo2 = StringField("Link to photo (optional)", validators=[validators.Optional(), validators.Length(max=199)])
    photo3 = StringField("Link to photo (optional)", validators=[validators.Optional(), validators.Length(max=199)])
    submit = SubmitField("Post")

class RegisterForm(FlaskForm):
    remail = StringField("Username", validators=[validators.Length(max=44)])
    rpassword = StringField("Password", validators=[reg_check, validators.Length(max=44)])
    rsubmit = SubmitField("Register")

class SearchForm(FlaskForm):
    search = StringField("Search")
    submit = SubmitField("Go!")

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['email'] = None
    return redirect(url_for("login"))

@app.route('/', methods=['GET', 'POST'])
def login():
    email = get_email()
    form = LoginForm()
    reg = RegisterForm()
    login_email = form.email.data
    login_password = form.password.data
    reg_email = reg.remail.data
    reg_password = reg.rpassword.data
    print('login')
    print(email)
    if get_email():
        return redirect(url_for("search"))
    if form.validate_on_submit():
        email = form.email.data
        set_cookie(email)
        password = form.password.data
        return redirect(url_for("search"))
    elif reg.validate_on_submit():
        email = reg.remail.data
        set_cookie(email)
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
    if not session.get('email'):
        return redirect(url_for("login"))
    form=SearchForm()
    return render_template("search.html", form=form)

@app.route('/postings_list', methods=['GET', 'POST'])
def postings_list():
    if not session.get('email'):
        return redirect(url_for("login"))
    email = get_email()
    print('posting_list')
    print(email)
    form=SearchForm()
    query_orig = form.search.data
    res = db.session.execute("select * from posts join buildings on posts.building = buildings.name")
    posts = res.fetchall()
    body=''
    results=[]
    print('posts')
    print(posts)
    for i in posts:
        if query_orig.lower() in i[1].lower() or query_orig.lower() in i[3].lower() or query_orig.lower() in i[2].lower():
            upload_id = i[4]
            query = "select url from images where upload_id = {}".format(upload_id)
            res = db.session.execute(query)
            imgs = res.fetchall()
            print('Images {}'.format(imgs))
            for j in range(len(imgs)):
                imgs[j] = imgs[j][0]
            lat = i[6]
            lon = i[7]
            title = i[1]
            desc = i[2]
            build = i[3]
            body="https://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels?pp="+str(lat)+","+str(lon)+";4;"+build+"&key=AvWjYu-PKLX_yA_wjaiVhhgn8L4zISfT_zN1cpFjwLyzByKro4crRk6pOE1r8fmI"
            print(body)
            email = i[0]
            results.append((body, title, desc, imgs, email))
    print('results')
    print(results)
    return render_template("postings_list.html", search_res=results)


@app.route('/new_posting', methods=['GET', 'POST'])
def new_posting():
    if not session.get('email'):
        return redirect(url_for("login"))
    email=get_email()
    print('new_posting')
    print(email)
    form = NewPost()
    if form.validate_on_submit() and form.title.data and form.review.data and form.building.data:
        query = "select id from posts order by id desc limit 1"
        res = db.session.execute(query)
        posts = res.fetchall()
        print(posts)
        ide = posts[0][0]+1

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
        
        query = "INSERT INTO posts VALUES ('{}', '{}', '{}', '{}', '{}', '{}');".format(email, form.title.data, form.review.data, form.building.data, ide, ide)
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for("search"))
    return render_template("new_post.html", form = form)
