import os
from flask import Blueprint, app,request,jsonify,g,flash,json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash

contact_bp = Blueprint('contact', __name__)


@contact_bp.get('/contact_us')
def contact_us():
    try:
        data = request.json
        first_name = data.get("first_name")
        last_name = data.get('last_name')
        subject = data.get('subject')
        description = data.get('description')
        email = data.get('email')

        if not data:
            return jsonify({'error': 'Do sign-up with all required data'}), 400
        elif not first_name:
            return jsonify({'error': 'Please Enter your First Name'}), 400
        elif not last_name:
            return jsonify({'error': 'Please Enter Your Last Name'}), 400
        elif not subject:
            return jsonify({'error': 'Please Enter Subject'}), 400
        elif not description:
            return jsonify({'error': 'Please Enter Description'}), 400
        elif not email:
            return jsonify({'error': 'Please Enter Email'}), 400

        cursor = g.db.cursor()
        cursor.execute(
            "INSERT INTO tbl_contact_us(first_name, last_name,subject,description,email) VALUES(%s, %s, %s, %s, %s)",
            (first_name, last_name, subject, description, email),

        )
        g.db.commit()
        return jsonify(
            {'message': f"Record Inserted Sucessfully"}), 201

    except Exception as e:
        return jsonify({'error': f'{e}'})
