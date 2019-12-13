"""
docstring
"""
from flask import Flask, render_template, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bmiller:@localhost:5432/world'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///world.db'
db = SQLAlchemy(app)


@app.route('/')
def all_countries():
    res = db.session.execute('select * from country')
    c_list = res.fetchall()
    cols = res.keys()
    print(c_list[0]['name'])
    curs = db.session.execute('select distinct continent from country')
    cont_list = curs.fetchall()

    return render_template('country_boot.html',
                           countries=c_list,
                           continents=cont_list,
                           columns=cols)

@app.route('/citylist/<c_code>')
def citylist(c_code):
    res = db.session.execute('select * from city where countrycode = :ccode',
                             {'ccode': c_code})
    return render_template('cities.html', cities=res.fetchall(),
                           columns=res.keys())

@app.route('/continent')
def countries_by_continent():
    continent = request.args['selected_continent']
    res = db.session.execute('select * from country where continent = :cont order by name',
                             {'cont': continent})
    c_list = res.fetchall()

    return render_template('country_boot.html',
                           countries=c_list,
                           continents=[],
                           columns=res.keys())


app.run(debug=True, port=8003, host="0.0.0.0")
