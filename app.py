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
    login_email = form.field.data
    if not (login_email in emails):
        raise ValidationError("Incorrect User Name or Password")
    
def pass_check(form, field):
    res = db.session.execute("select pass_word from users")
    passwords = res.fetchall()
    login_password = form.field.data
    if not (login_password in passwords):
        raise ValidationError("Incorrect User Name or Password")

def reg_check(form, field):
    res = db.session.execute("select email from users")
    emails = res.fetchall()
    login_email = form.field.data
    if (login_email in emails):
        raise ValidationError("Username taken")
    
class LoginForm(FlaskForm):
    email = StringField("User Name", validators=login_check)
    password = StringField("Password", validators=pass_check)
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    remail = StringField("User Name", validators=reg_check)
    rpassword = StringField("Password")
    rsubmit = SubmitField("Register")
    
csrf = CSRFProtect()
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    
    global email
    global password
    form = LoginForm()
    reg = RegisterForm()
    res = db.session.execute("select email from users")
    emails = res.fetchall()
    res = db.session.execute("select pass_word from users")
    passwords = res.fetchall()
    print(emails)
    print(passwords)
    login_email = form.email.data
    login_password = form.password.data
    reg_email = reg.remail.data
    reg_password = reg.rpassword.data
    if form.validate_on_submit() and login_email and login_password:
        print('1')
        print(login_email)
        print(login_password)
        print(reg_email)
        print(reg_password)
        email = form.email.data
        password = form.password.data
        res = db.session.execute("select email from users")
        emails = res.fetchall()
        res = db.session.execute("select pass_word from users")
        passwords = res.fetchall()
        if not (email in emails and password in passwords):
            return redirect(url_for('login')) #render_template("login.html", form=form, reg=reg)

    if reg.validate_on_submit() and reg_email and reg_password:
        print('2')
        print(login_email)
        print(login_password)
        print(reg_email)
        print(reg_password)
        email = reg.remail.data
        password = reg.rpassword.data
        res = db.session.execute("select email from users")
        emails = res.fetchall()
        if not (email in emails):
            query = "INSERT INTO users VALUES ('{}', '{}');".format(email, password)
            print(query)
            db.session.execute(query)
            db.session.commit()
            return redirect(url_for('login'))

##@app.route('/index')
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
