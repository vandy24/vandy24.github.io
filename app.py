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
    if form.validate_on_submit() and login_email and login_password:
        email = form.email.data
        password = form.password.data
        return render_template("search.html", form=SearchForm())
    elif reg.validate_on_submit() and reg_email and reg_password:
        email = reg.remail.data
        password = reg.rpassword.data
        res = db.session.execute("select email from users")
        emails = res.fetchall()
        query = "INSERT INTO users VALUES ('{}', '{}');".format(email, password)
        db.session.execute(query)
        db.session.commit()
        return redirect(url_for('login'))
    else: return render_template("login.html", form=form, reg=reg)

@app.route('/search', methods=['GET', 'POST'])
def search():
    form=SearchForm()
    if form.validate_on_submit():
        results=[]
        query = form.search.data
        res = db.session.execute("select * from postings")
        postings = res.fetchall()
        for posting in postings:
            if query == '':
                results = postings
                break
            if query in posting[1] or query in posting[2]:
                results.append(posting)
        print(results)
        #return render_template("posting_list.html", postings = results)
    return render_template("search.html", form=form)
        
        
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
