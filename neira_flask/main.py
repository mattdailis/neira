import json
import os
from flask import Flask, jsonify, render_template, request
from . import db

HERE = os.path.dirname(__file__)

app = Flask(__name__, static_url_path='/static')

@app.route("/")
def root():
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/category.html")
def category():
    return render_template("category.html")

@app.route("/api/races")
def api():
    # year = request.args.get('year')
    # db.main()
    with open(os.path.join(HERE,"static/data/races-index-2025-tmp.json")) as f:
        return jsonify(json.load(f))
