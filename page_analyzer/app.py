from flask import render_template
from flask import Flask
from dotenv import load_dotenv

import os


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


@app.route('/')
def index():
    return render_template('index.html')
