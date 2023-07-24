import os
from flask import Blueprint, app, request, jsonify, g, flash, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

static_bp = Blueprint('static', __name__)


@static_bp.get("/faq")
def faq():
    cursor = g.db.cursor(dictionary=True)
    cursor.execute("SELECT question,answer from  tbl_faq")
    faqq = cursor.fetchall()
    return jsonify({"FAQ": faqq}), 400


@static_bp.get("/terms_condition")
def terms_condition():
    cursor = g.db.cursor(dictionary=True)
    cursor.execute("SELECT  terms_condition from  tbl_setting")
    faqq = cursor.fetchall()
    return jsonify({"Terms  & Privacy Policy": faqq}), 400


@static_bp.get("/about")
def about():
    cursor = g.db.cursor(dictionary=True)
    cursor.execute("SELECT  about_us from  tbl_setting")
    faqq = cursor.fetchall()
    return jsonify({"About Us": faqq}), 400
