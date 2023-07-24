import os
from flask import Blueprint, app,request,jsonify,g,flash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash



business_details_bp= Blueprint('business',__name__)
blacklist=set()



@business_details_bp.post('/restourent_review/<int:res_id>')
@jwt_required()
def restourent_review(res_id):
    try:
        u_id=get_jwt_identity()
        cursor=g.db.cursor(dictionary=True)
        cursor.execute (f"SELECT (SELECT profile_picture from tbl_user WHERE id={u_id}) as User_Profile,tu.id,tu.total_like,tu.avg_rating,tu.profile_picture,tu.company_name,tu.address,tr.comments,tr.created_t FROM tbl_user tu JOIN tbl_rating tr ON tu.id=tr.merchant_id WHERE user_type='MERCHANT'and tu.id={res_id} ORDER BY tr.id DESC LIMIT 1")
        user=cursor.fetchone() 
        return  jsonify({'message':user}), 201
    except Exception as e:
        return jsonify({"Error": str(e) }),400
    
@business_details_bp.post('/restourent_review_raaves/<int:res_id>')
@jwt_required()
def restourent_review_raaves(res_id):
    try:
        u_id=get_jwt_identity()
        cursor=g.db.cursor(dictionary=True)
        cursor.execute (f"select tbl_rating.rating,tbl_rating.comments,tbl_rating.created_t,tbl_rating.upload_image, tbl_rating_like_user.like_about_id FROM tbl_rating JOIN tbl_rating_like_user ON tbl_rating.user_id=tbl_rating_like_user.user_id and tbl_rating.merchant_id=tbl_rating_like_user.res_id WHERE tbl_rating.user_id={u_id} AND tbl_rating.merchant_id ={res_id}")
        user=cursor.fetchone() 
        return  jsonify({'message':user}), 201
    except Exception as e:
        return jsonify({"Error": str(e) }),400
