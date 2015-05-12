from flask import Flask, render_template
from datetime import datetime

import config
import Database

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')


@app.template_filter('timestamp2date')
def timestamp2date(timestamp):
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')


@app.route("/")
def hello():
    db = Database.Database()
    return render_template('index.html',
                           sensors=db.get(),
                           config=config)

