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
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///final.db'
db = SQLAlchemy(app)
email = None
password = None

class LoginForm(FlaskForm):
    email = StringField("Email")
    password = StringField("Password")
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    remail = StringField("Email")
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
    res = db.session.execute("select email from user")
    emails = res.fetchall()
    res = db.session.execute("select password from user")
    passwords = res.fetchall()
    print(emails)
    print(passwords)
    login_email = form.email.data
    login_password = form.password.data
    reg_email = reg.remail.data
    reg_password = reg.rpassword.data

    print(login_email)
    print(login_password)
    print(reg_email)
    print(reg_password)
    if form.validate_on_submit() and login_email and login_password:
        print('1')
        print(login_email)
        print(login_password)
        print(reg_email)
        print(reg_password)
        email = form.email.data
        password = form.password.data
        res = db.session.execute("select email from user")
        emails = res.fetchall()
        res = db.session.execute("select password from user")
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
        res = db.session.execute("select email from user")
        emails = res.fetchall()
        if not (email in emails):
            query = "INSERT INTO user VALUES ('{}', '{}');".format(email, password)
            print(query)
            db.session.execute(query)
            return redirect(url_for('login')) #
    else: return render_template("login.html", form=form, reg=reg)

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
