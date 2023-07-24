import os
from flask import Blueprint, app, request, jsonify, g, flash
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

user_bp = Blueprint('user', __name__)
blacklist = set()


@user_bp.get('/restourent_review/<int:res_id>')
@jwt_required()
def restourent_review(res_id):
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT (SELECT profile_picture from tbl_user WHERE id={u_id}) as User_Profile,tu.id,tu.total_like,tu.avg_rating,tu.profile_picture,tu.company_name,tu.address,tr.comments,tr.created_t FROM tbl_user tu JOIN tbl_rating tr ON tu.id=tr.merchant_id WHERE user_type='MERCHANT'and tu.id={res_id} ORDER BY tr.id DESC LIMIT 1")
        user = cursor.fetchone()
        return jsonify({'message': user}), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/restourent_review_raaves/<int:res_id>')
@jwt_required()
def restourent_review_raaves(res_id):
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f"select tbl_rating.rating,tbl_rating.comments,tbl_rating.created_t,tbl_rating.upload_image, tbl_rating_like_user.like_about_id FROM tbl_rating JOIN tbl_rating_like_user ON tbl_rating.user_id=tbl_rating_like_user.user_id and tbl_rating.merchant_id=tbl_rating_like_user.res_id WHERE tbl_rating.user_id={u_id} AND tbl_rating.merchant_id ={res_id}")
        user = cursor.fetchall()
        return jsonify({'message': user}), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 400




@user_bp.post('/restourent_review_insert/<int:res_id>')
@jwt_required()
def restourent_review_insert(res_id):
    try:
        u_id = get_jwt_identity()
        data = request.json
        rating = data.get("rating")
        x = (float(rating))
        comment = data.get("comment")
        upload_image = data.get("upload_image")
        like = data.get("like")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE user_type='MERCHANT'and id ={res_id}")
        res = cursor.fetchone() 
        print("--------------------------->",res)
        if res:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `tbl_rating` WHERE user_id={u_id} and merchant_id ={res_id}")
            rating = cursor.fetchone()
            if rating:
                cursor = g.db.cursor()
                cursor.execute(
                    f"UPDATE tbl_rating SET rating={x},comments='{comment}',upload_image='{upload_image}' WHERE user_id={u_id} AND merchant_id={res_id}")
                g.db.commit()
                return jsonify({"Message": "successfull UPDATE review"}), 200

            cursor = g.db.cursor()
            cursor.execute(
                f"INSERT INTO tbl_rating (user_id,rating,merchant_id,comments,upload_image) VALUES ({u_id},{x},{res_id},'{comment}','{upload_image}')")
            coin = 5
            cursor.execute(f"INSERT INTO tbl_coin (user_id,marchant_id,coin) VALUES ({u_id},{res_id},{coin})")  
            g.db.commit()
            cursor = g.db.cursor(dictionary=True)
            for i in like:
                cursor.execute(f"""INSERT INTO tbl_rating_like_user (like_about_id,user_id,res_id)
                SELECT id,{u_id},{res_id}
                FROM tbl_like_about WHERE id= {i} """)
            g.db.commit()
            return jsonify({"Message": f"successfull inserted review you earn {coin} !!! "}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.post('/restourent_review_like_insert/<int:res_id>')
@jwt_required()
def restourent_review_like_insert(res_id):
    try:
        u_id = get_jwt_identity()
        data = request.json
        like = data.get("like")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE user_type='MERCHANT'and id ={res_id}")
        res = cursor.fetchone()
        if res:
            cursor = g.db.cursor(dictionary=True)
            for i in like:
                cursor.execute(f"""INSERT INTO tbl_rating_like_user (like_about_id,user_id,res_id)
                SELECT id,{u_id},{res_id}
                FROM tbl_like_about WHERE id= {i} """)
            g.db.commit()
            return jsonify({"Message": "like review inserted"}), 200
        else:
            return jsonify({"Error": "restorent not found"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400





@user_bp.post('/report_review_B/<int:res_id>')
@jwt_required()
def restourent_review_B(res_id):
    try:
        u_id = get_jwt_identity()
        data = request.json
        report_type = data.get("report_type")
        description = data.get("description")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE user_type='MERCHANT'and id ={res_id}")
        user = cursor.fetchone()
        if user:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM tbl_report WHERE  merchant_id={res_id} and user_id={u_id}")
            user = cursor.fetchone()
            if not user:
                cursor = g.db.cursor(dictionary=True)
                cursor.execute(
                    f"INSERT INTO tbl_report (user_id,merchant_id,report_type,description) VALUES ( {u_id},{res_id},'{report_type}','{description}')")
                g.db.commit()
                return jsonify({'message': "Report added successfully"}), 201
            return jsonify({'message': "Report added in past"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.post('/report_review_U/<int:res_id>')
@jwt_required()
def report_review_U(res_id):
    try:
        print(res_id)
        u_id = get_jwt_identity()
        data = request.json
        report_type = data.get("report_type")
        description = data.get("description")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE  user_type='CUSTOMER' and id ={res_id}")
        user = cursor.fetchone()
        if not user:
            return jsonify({'message': "user not found"}), 400
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM tbl_report WHERE merchant_id={res_id} and user_id={u_id}")
        user = cursor.fetchone()
        if not user:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute(
                f"INSERT INTO tbl_report (user_id,merchant_id,report_type,description) VALUES ( {u_id},{res_id},'{report_type}','{description}')")
            g.db.commit()
            return jsonify({'message': "Report added successfully"}), 201
        return jsonify({'message': "Report added in past"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.post('/user_follow')
@jwt_required()
def user_follow():
    try:
        u_id = get_jwt_identity()
        data = request.json
        follow_to = data.get("follow_to")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE id ={follow_to}")
        user = cursor.fetchone()
        if u_id == follow_to:
            return jsonify({'message': "Self request not allow"}), 400
        if user:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM `tbl_follow_following` WHERE user_id_1 ={u_id} and user_id_2 ={follow_to}")
            user = cursor.fetchone()
            if not user:
                cursor = g.db.cursor(dictionary=True)
                cursor.execute(f"INSERT into tbl_follow_following (user_id_1 ,user_id_2) values ({u_id},{follow_to})")
                g.db.commit()
                return jsonify({'message': f"{u_id} send request to {follow_to}"}), 201
            return jsonify({'message': "Already requested"}), 400
        return jsonify({'message': "user not found"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/user_following')
@jwt_required()
def user_following():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT u.profile_picture, CONCAT(u.f_name,u.l_name) as username, ff.user_id_2 ,ff.user_status  FROM `tbl_follow_following` ff 
                    JOIN tbl_user u on ff.user_id_1 = u.id
                    WHERE ff.user_id_2 ={u_id}  and user_status ='Pending' """)
        user = cursor.fetchall()
        return jsonify({'message': user}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/user_follow_req')
@jwt_required()
def user_follow_req():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT u.profile_picture, CONCAT(u.f_name,u.l_name) as username, ff.user_id_2 ,ff.user_status  FROM `tbl_follow_following` ff 
                    JOIN tbl_user u on ff.user_id_1 = u.id
                    WHERE ff.user_id_1 ={u_id} and ff.user_status ='Pending'""")
        user = cursor.fetchall()
        return jsonify({'message': user}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/user_following_req')
@jwt_required()
def user_following_req():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT u.profile_picture, CONCAT(u.f_name,u.l_name) as username, ff.user_id_2 ,ff.user_status  FROM `tbl_follow_following` ff 
                    JOIN tbl_user u on ff.user_id_1 = u.id
                    WHERE ff.user_id_2 ={u_id}  and user_status ='Pending' """)
        user = cursor.fetchall()

        return jsonify({'message': user}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/user_following_req_approved')
@jwt_required()
def user_following_req_approved():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT u.profile_picture, CONCAT(u.f_name," ",u.l_name) as username, ff.user_id_2 ,ff.user_status  FROM `tbl_follow_following` ff 
                    JOIN tbl_user u on ff.user_id_1 = u.id
                    WHERE ff.user_id_2 ={u_id}  and user_status ='Accept' """)
        user = cursor.fetchall()
        return jsonify({'message': user}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.patch('/user_following_req_aprove/<id>')
@jwt_required()
def user_following_req_aprove(id):
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"""SELECT u.profile_picture, CONCAT(u.f_name,u.l_name) as username, ff.user_id_2 ,ff.user_status  FROM `tbl_follow_following` ff 
                    JOIN tbl_user u on ff.user_id_1 = u.id
                    WHERE ff.user_id_2 ={id}  and ff.user_id_1 ={u_id} and user_status ='Pending' """)
        user = cursor.fetchone()
        if user:
            cursor = g.db.cursor()
            cursor.execute(
                f"UPDATE tbl_follow_following SET user_status='Accept' WHERE user_id_2 ={id} AND user_id_1 ={u_id} ")
            g.db.commit()
            return jsonify({'message': "accepted successfully"}), 201
        return jsonify({'Error': "request not found"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@user_bp.get('/user_profile')
@jwt_required()
def user_profile():
    user_id = get_jwt_identity()
    try:
        cursor = g.db.cursor()
        cursor.execute(
            f"SELECT u.profile_picture,u.company_name as User_Name,(SELECT COUNT(user_id_2) FROM tbl_follow_following WHERE user_id=user_id AND user_status='Accept') as Follower ,SUM(cc.coin) FROM tbl_user u JOIN tbl_coin cc ON cc.user_id=u.id WHERE u.id = {user_id}")
        user = cursor.fetchone()
        return jsonify({"profile_picture": user[0],
                        "User_Name": user[1],
                        "followers": user[2],
                        "Coin": user[3]}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400


@user_bp.post('/edit_profile')
@jwt_required()
def edit_profile():
    user_id = get_jwt_identity()
    cursor = g.db.cursor()
    cursor.execute(f"SELECT * from tbl_user where id = '{user_id}' ")
    user = cursor.fetchone()
    if user:
        try:
            user_id = get_jwt_identity()
            data = request.json
            if not data:
                return jsonify({'message': 'data not found'}), 400

            f_name = data.get('f_name')
            l_name = data.get('l_name')
            email = data.get('email')
            mobile_no = data.get('mobile_no')

            cursor = g.db.cursor()
            cursor.execute("SELECT * FROM tbl_user WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                try:
                    query = "UPDATE tbl_user SET f_name = %s, l_name = %s, email = %s, number = %s  WHERE id = %s"
                    cursor.execute(query, (f_name, l_name, email, mobile_no, user_id))
                    g.db.commit()
                    return jsonify({'message': 'Profile Edit Sucessfull'})
                except Exception as e:
                    return jsonify({'message': str(e)}), 400

            else:
                return jsonify({'message': 'user not found'}), 400

        except Exception as e:
            return jsonify({'message': str(e)}), 400
    return jsonify({'Error': "request not found"}), 200