from flask import Flask, render_template, g
from datetime import datetime

import config
import Database

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')


@app.before_request
def before_request():
    g.db = Database.Database()


@app.template_filter('timestamp2date')
def timestamp2date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


@app.route('/')
def index():
    return render_template('index.html',
                           data=g.db.get())


@app.route('/detail/<node>', defaults={'sensor': None})
@app.route('/detail/<node>/<sensor>')
def detail(node, sensor):
    if sensor:
        data = (g.db.get(node=node, sensor=sensor),)
    else:
        data = g.db.get(node=node, sensor=sensor)

    return render_template('nodedetail.html',
                           data=data,
                           config=config)
