"""
docstring
"""
from flask import Flask, render_template, request, g
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
    email = StringField("Email")
    password = StringField("Password")
    submit = SubmitField("Register")
    
csrf = CSRFProtect()
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)


@app.route('/', methods=['GET', 'POST'])
def login():
    global email
    global password
    form = LoginForm()
    reg = RegisterForm()
    if form.validate_on_submit():
        email = form.email
        password = form.password
        res = db.session.execute("select email from user")
        emails = res.fetchall()
        res = db.session.execute("select password from user")
        passwords = res.fetchall()
        if not (email in emails and password in passwords):
            return render_template("login.html", form=form, reg=reg)
    else: return render_template("login.html", form=form, reg=reg)
    
    if reg.validate_on_submit():
        email = reg.email
        password = reg.password
        res = db.session.execute("select email from user")
        emails = res.fetchall()
        if not (email in emails):
            db.session.execute(user.insert(), email=email, password=password)
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
