import logging
import os

from flask import Flask, jsonify, render_template, request, g

from neira_flask.checksum import compute_checksum

from . import db
from neira_flask.auth import requires_auth, user_has_scope

logger = logging.getLogger(__name__)

HERE = os.path.dirname(__file__)

app = Flask(__name__, static_url_path='/static')
print("Started app!")

@app.route("/")
def root():
    logger.debug('root route called')
    return render_template("index.html")

@app.route("/index.html")
def index():
    return render_template("index.html")

@app.route("/category.html")
def category():
    return render_template("category.html")

@app.route("/review.html")
def review():
    return render_template("review.html")

@app.route("/review-regatta.html")
def review_regatta():
    return render_template("review-regatta.html")

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


@app.route("/api/test")
@requires_auth
def api_test():
    if user_has_scope('review'):
        return jsonify("success, " + str(g.current_user))
    else:
        return jsonify("failure, " + str(g.current_user))

@app.route("/api/regattas")
def api_regattas():
    return jsonify(db.get_regattas_review_status(2025))

@app.route("/api/review-regatta")
def api_regatta():
    uid = request.args.get('uid')
    if uid is None:
        return "uid query parameter is required", 400
    all_corrections = db.get_corrections()
    regattas = db.get_regatta_for_review(uid)
    return jsonify({
        "regatta": regattas,
        "corrections": all_corrections[uid],
        "checksums": { status: (4, regatta["checksum"]) for status, regatta in regattas.items() }
    })

@app.route("/api/save-corrections", methods=["POST"])
@requires_auth
def save_corrections():
    if not user_has_scope('edit:corrections'):
        return jsonify({"status": "unauthorized"}), 403
    
    content = request.get_json()
    regatta_uid = content["regatta_uid"]
    checksum = content["checksum"]
    details = content["details"]
    correction_id = db.insert_correction_single(regatta_uid, checksum, details)
    logger.info("inserted %s %s %s", regatta_uid, checksum, details)

    db.insert_job("apply_corrections", {"uid": regatta_uid, "correction_id": correction_id})

    return jsonify({
        "status": "success",
        "correction_id": correction_id
    })

    
