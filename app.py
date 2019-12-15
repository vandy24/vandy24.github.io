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
from wtforms import StringField, SubmitField, SelectField, validators
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
    elif reg.validate_on_submit() and reg_email and reg_password or email:
        email = reg.remail.data
        password = reg.rpassword.data
        res = db.session.execute("select email from users")
        emails = res.fetchall()
        query = "INSERT INTO users VALUES ('{}', '{}');".format(email, password)
        db.session.execute(query)
        db.session.commit()
    else: return render_template("login.html", form=form, reg=reg)

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
        
@app.route('/postings_list', methods=['GET', 'POST'])
def search():
    form=SearchForm()
    return render_template("search.html", form=form)

@app.route('/postings_list', methods=['GET', 'POST'])
def postings_list():
    form=SearchForm()
    print(form.search.data)
    print(bool(form.validate_on_submit()))
    query = form.search.data
    res = db.session.execute("select * from posts join buildings on posts.building = buildings.building")
    posts = res.fetchall()
    print(posts)
    body=''
    results=[]
    for i in posts:
        if query.lower() in i[1].lower():
            upload_id = i[4]
            query = "select url from imgs where upload_id = {}".format(upload_id)
            res = db.session.execute(query)
            imgs = res.fetchall()
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
                
##def citylist(c_code):
##    res = db.session.execute('select * from city where countrycode = :ccode',
##                             {'ccode': c_code})
##    return render_template('cities.html', cities=res.fetchall(),
##                           columns=res.keys())

##@app.route('/continent')
##@login_required
##def countries_by_continent():
##    continent = request.args['selected_continent']
##    res = db.session.execute('select * from country where continent = :cont order by name',
##                             {'cont': continent})
##    c_list = res.fetchall()
##
##    return render_template('country_boot.html',
##                           countries=c_list,
##                           continents=[],
##                           columns=res.keys())
