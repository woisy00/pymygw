from logging import getLogger
from flask import Flask

import config
import Database

app = Flask(__name__)

@app.route("/")
def hello():
        return "Hello World!"

