from flask import Flask, render_template

import config
import Database

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')

@app.route("/")
def hello():
    db = Database.Database()
    return render_template('index.html',
                           sensors=db.get())

