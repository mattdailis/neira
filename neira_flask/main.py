import json
import logging
import os
from flask import Flask, jsonify, render_template, request
from . import db

HERE = os.path.dirname(__file__)

app = Flask(__name__, static_url_path='/static')
print("Started app!")

@app.route("/")
def root():
    logging.debug('root route called')
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/category.html")
def category():
    return render_template("category.html")

@app.route("/api/races")
def api_races():
    # year = request.args.get('year')
    # db.main()
    with open(os.path.join(HERE,"static/data/races-index-2025-tmp.json")) as f:
        return jsonify(json.load(f))

@app.route("/api/heats")
def api_heats():
    year = request.args.get('year')
    class_ = request.args.get('class')
    gender = request.args.get('gender')
    varsity_index = request.args.get('varsity_index')
    if year is None or class_ is None or gender is None or varsity_index is None:
        return "year, class_, gender, and varsity_index query parameters are required", 400
    heats = db.get_heats(year=2025, class_=class_, gender=gender, varsity_index=varsity_index)
    return jsonify(heats)
