from flask import Flask, request, Response, render_template
import requests
import itertools
import os
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, validators
from wtforms.validators import Regexp, Required, ValidationError
import re

class Op(validators.Optional):
    # a validator which makes a field optional if
    # another field has a desired value

    def __init__(self, other_field_name, *args, **kwargs):
        self.other_field_name = other_field_name
        super(Op, self).__init__(*args, **kwargs)

    def __call__(self, form, field):
        other_field = form._fields.get(self.other_field_name)
        if bool(other_field.data):
            super(Op, self).__call__(form, field)

def len_check(form, field):
    other_field=form._fields.get('length')
    if len(field.data)!=other_field.data and other_field.data!=26 and bool(field.data):
        raise ValidationError("Pattern must match length")
    
    
class WordForm(FlaskForm):
    
    avail_letters = StringField("Letters", validators= [Op("pattern"),
        Regexp(r'^[a-z]+$', message="must contain letters only")
    ])
    
    length = SelectField('Max length',
                           choices=[(26, 'Max'), (3, 3), (4, 4), (5,5),
                                    (6, 6), (7, 7), (8,8), (9, 9), (10,10)],
                         default=(26, 'Max'), coerce=int)
    
    pattern = StringField("Pattern",
                          validators= [Op("avail_letters"), len_check,
                                       Regexp(r'^[\.a-z\.*]+$',
                                              message="must contain letters or '.' only")])

    submit = SubmitField("Go")


csrf = CSRFProtect()
app = Flask(__name__)
app.config["SECRET_KEY"] = "row the boat"
csrf.init_app(app)

@app.route('/')
def index():
    form = WordForm()
    return render_template("index.html", name="Peter Van Dyke", form=form)


@app.route('/words', methods=['POST','GET'])
def letters_2_words():

    form = WordForm()
    if form.validate_on_submit():
        letters = form.avail_letters.data
        if not letters:
            letters = "abcdefghijklmnopqrstuvwxyz"
        length = int(form.length.data)
        pattern = form.pattern.data
        no_pattern=False
        if not pattern:
            pattern = ".*"
            no_pattern=True
    else:
        return render_template("index.html", name="Peter Van Dyke", form=form)

    with open('sowpods.txt') as f:
        good_words = set(x.strip().lower() for x in f.readlines())

    word_set = set()
    if not no_pattern and len(pattern)<length:
        length=len(pattern)
    pattern = re.compile(pattern)
    for l in range(3,length+1):
        for word in itertools.permutations(letters,l):
            w = "".join(word)
            if pattern.match(w):
                if w in good_words:
                    if len(w)<=length:
                        word_set.add(w)
    wordlist = sorted(word_set)
    return render_template('wordlist.html',
        wordlist=wordlist, key="5f494129-e5d2-4c7b-9171-6498252fdbb7",
        name="Peter Van Dyke")




@app.route('/proxy')
def proxy():
    result = requests.get(request.args['url'])
    resp = Response(result.text)
    resp.headers['Content-Type'] = 'application/json'
    return resp


