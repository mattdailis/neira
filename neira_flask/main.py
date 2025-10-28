from flask import Flask, render_template
import os

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def hello_world():
    return render_template("index.html")

@app.route("/category.html")
def category():
    return render_template("category.html")
