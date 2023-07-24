import os
from flask import Blueprint, app, request, jsonify, g, flash, json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import jsonify
from datetime import datetime, time
import random

resraurant_aboutus_bp = Blueprint('resraurant_aboutus', __name__)
blacklist = set()


@resraurant_aboutus_bp.get('/restaurent_fevorite')
@jwt_required()
def restaurent_fevorite():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f"select tbl_user.company_name,tbl_user.address,tbl_user.profile_picture,tbl_user.total_like,tbl_user.avg_rating ,tbl_rating.rating FROM tbl_user  JOIN tbl_rating ON tbl_rating.user_id= tbl_user.id WHERE tbl_rating.user_id={u_id} AND tbl_rating.rating > 4;")
        user = cursor.fetchall()
        return jsonify({'message': user}), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@resraurant_aboutus_bp.get('/restaurent_my_raaves')
@jwt_required()
def restaurent_my_raaves():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f"select tbl_user.company_name,tbl_user.address,tbl_user.profile_picture,tbl_rating.rating,tbl_rating.comments,tbl_rating.created_t,tbl_rating.upload_image, tbl_rating_like_user.like_about_id FROM tbl_rating JOIN tbl_rating_like_user ON tbl_rating.user_id=tbl_rating_like_user.user_id AND tbl_rating.merchant_id=tbl_rating_like_user.res_id JOIN tbl_user ON tbl_rating.merchant_id= tbl_user.id WHERE tbl_rating.user_id={u_id}")
        user = cursor.fetchall()
        return jsonify({'message': user}), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@resraurant_aboutus_bp.post('/restourent_review_insert_24h/<int:res_id>')
@jwt_required()
def restourent_review_insert_24h(res_id):
    try:
        u_id = get_jwt_identity()
        data = request.json
        rating = data.get("rating")
        x = (float(rating))
        comment = data.get("comment")
        upload_image = data.get("upload_image")
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `tbl_user` WHERE user_type='MERCHANT'and id ={res_id}")
        res = cursor.fetchone()
        print(res)
        if res:
            cursor = g.db.cursor(dictionary=True)
            cursor.execute(
                f"SELECT * FROM `tbl_rating` WHERE user_id={u_id} and merchant_id ={res_id} and created_t >= NOW() - INTERVAL 1 DAY")
            rating = cursor.fetchone()
            if rating:
                cursor = g.db.cursor()
                cursor.execute(
                    f"UPDATE tbl_rating SET rating={x},comments='{comment}',upload_image='{upload_image}',update_at= NOW() WHERE user_id={u_id} AND merchant_id={res_id}")
                g.db.commit()
                return jsonify({"Message": "successfull UPDATE review"}), 200
            return jsonify({"Error": "sorry can not modify reviview"}), 400
        return jsonify({"Message": "review not UPDATED "}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@resraurant_aboutus_bp.get('/gold_coin_history')
@jwt_required()
def gold_coin_history():
    try:
        u_id = get_jwt_identity()
        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f"SELECT tbl_user.company_name,tbl_user.profile_picture,tbl_coin.coin,tbl_coin.created_at FROM `tbl_coin`JOIN tbl_user ON tbl_coin.marchant_id=tbl_user.id WHERE user_id={u_id} ORDER BY tbl_coin.id DESC")
        res = cursor.fetchall()
        return jsonify({'message': res}), 201
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@resraurant_aboutus_bp.post("/refer_friend")
@jwt_required()
def refer_friend():
    try:
        u_id = get_jwt_identity()
        email = request.json.get('email')
        if email != "":
            cursor = g.db.cursor()
            cursor.execute(f"SELECT * FROM tbl_user WHERE  email='{email}'")
            user = cursor.fetchone()
            if not user:
                r1 = 10
                x = (random.randrange(1111111111, 9999999999, r1))
                p = str(x)
                hash_password = generate_password_hash(p, method='sha256', salt_length=8)
                url = "http://127.0.0.1:8000/refer_friend_invition_accept"
                body = f"{url}/{hash_password}"

                from project import mail
                mail.send_message('New Message',
                                  sender='sonishreeji09@gmail.com',
                                  recipients=['sonishreeji09@gmail.com'],
                                  body=body
                                  )
                cursor = g.db.cursor()
                cursor.execute(
                    f"INSERT INTO tbl_refer_fraiend (user_id,refer_code,refer_email) VALUES ({u_id},'{hash_password}','{email}')")
                g.db.commit()
                return jsonify({"message": "successful"}), 200
            return jsonify({"message": "registered user can not use this founctionality"}), 400
        return jsonify({'message': ' Enter correct email'}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@resraurant_aboutus_bp.post("/refer_friend_invition_accept/<tokan>/<email>")
def refer_friend_invition_accept(tokan, email):
    try:
        cursor = g.db.cursor(buffered=True)
        cursor.execute(f"SELECT user_id,refer_code,count(user_id) FROM tbl_refer_fraiend WHERE refer_email='{email}'")
        user = cursor.fetchone()
        if not user:
            return jsonify({"Error": "user not found"}), 400
        if user:
            if user:
                print(user)
                # x = (user[3])
                # if x != email:
                #     return jsonify({'Error': "review added in the past"}), 400
                p = user[1]
                print(p)
                print(tokan)
                if p == tokan:
                    cursor = g.db.cursor(buffered=True)
                    coin = 50
                    cursor.execute(f"INSERT INTO tbl_coin (user_id,coin) VALUES ({user[0]},{coin})")
                    g.db.commit()
                    return jsonify({"msg": f"goldcoin {coin} successfully addend"}), 200
                return jsonify({"Error": "Data dose not march"}), 400
        return jsonify({"Error": "user not found"}), 400
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

# @resraurant_aboutus_bp.get('/restaurent_about/<res_id>')
# @jwt_required()
# def restaurent_about(res_id):
#     try:
#         cursor=g.db.cursor(dictionary=True)
#         cursor.execute (f"SELECT about_resturant FROM tbl_resturant WHERE id={res_id}")
#         user=cursor.fetchone() 
#         if not user:
#             return jsonify({"Error":" restaurent not valid"}),400
#         return jsonify({'message':user}), 201
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400


# @resraurant_aboutus_bp.get('/restaurent_menu/<res_id>')
# @jwt_required()
# def restaurent_menu(res_id):
#     try:
#         cursor=g.db.cursor(dictionary=True)
#         cursor.execute (f"SELECT tbl_food.food_name,tbl_food.food_image,tbl_food.food_price,tbl_resturant.resturant_name FROM `tbl_food`JOIN tbl_resturant ON tbl_food.resturant_id=tbl_resturant.id WHERE tbl_food.resturant_id={res_id}")
#         user=cursor.fetchall() 
#         if not user:
#             return jsonify({"Error":" restaurent not valid"}),400
#         return jsonify({'message':user}), 201
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400


# @resraurant_aboutus_bp.post('/restaurent_review')
# @jwt_required()
# def restaurent_review():
#     try:
#         u_id=get_jwt_identity()
#         restaurent_id=request.json.get("restaurent_id")
#         review=request.json.get("review")
#         cursor=g.db.cursor()
#         cursor.execute (f"SELECT count(user_id) FROM `tbl_resturant_review` WHERE  user_id={u_id} AND resturant_id={restaurent_id}")
#         user=cursor.fetchone()
#         x=(user[0])
#         if  x >= 1 :
#             return jsonify({'Error':"review added in the past"}), 400 
#         elif x == 0:
#             cursor=g.db.cursor()
#             cursor.execute (f"INSERT INTO tbl_resturant_review(user_id,resturant_id,review) VALUES ({u_id},{restaurent_id},'{review}')")
#             g.db.commit()
#             return jsonify({'message':"review added successfully"}), 201 
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400  

# @resraurant_aboutus_bp.post('/restaurent_rateing')
# @jwt_required()
# def restaurent_rateing():
#     try:
#         u_id=get_jwt_identity()
#         print(u_id)
#         restaurent_id=request.json.get("restaurent_id")
#         rating=request.json.get("rating")
#         cursor=g.db.cursor()
#         cursor.execute (f"SELECT count(user_id) FROM `tbl_resturant_rating` WHERE  user_id={u_id} AND resturant_id={restaurent_id}")
#         user=cursor.fetchone()
#         x=(user[0])
#         if  x >= 1 :
#             return jsonify({'Error':"rating added in the past"}), 400 
#         elif x == 0:
#             cursor=g.db.cursor()
#             cursor.execute (f"INSERT INTO tbl_resturant_rating(user_id,resturant_id,rate) VALUES ({u_id},{restaurent_id},'{rating}')")
#             g.db.commit()
#             return jsonify({'message':"Rating added successfully"}), 201 
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400  


# @resraurant_aboutus_bp.get('/restaurent_like')
# @jwt_required()
# def restaurent_like():
#     try:
#         data=request.json
#         restaurent_id=data.get("restaurent_id")
#         u_id=get_jwt_identity()
#         cursor=g.db.cursor()
#         cursor.execute (f"SELECT * FROM `tbl_resturant_like` WHERE is_active=0 AND is_delete=1 AND user_id={u_id} AND resturant_id={restaurent_id}")
#         user=cursor.fetchall()
#         print(user) 
#         if user:
#             g.db.commit()
#             cursor=g.db.cursor()
#             cursor.execute (f"UPDATE tbl_resturant_like SET is_active=1 , is_delete=0 WHERE user_id ='{u_id} AND resturant_id={restaurent_id}'")
#             g.db.commit()
#             return jsonify({'message':"like successfully"}), 201 
#         elif not user:
#             cursor=g.db.cursor()
#             cursor.execute (f"INSERT into tbl_resturant_like( user_id,resturant_id) VALUES ({u_id},{restaurent_id})")
#             g.db.commit()
#             return jsonify({'Error':"privious liked by user"}), 200 
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400  


# @resraurant_aboutus_bp.patch('/restaurent_like_update')   
# @jwt_required()
# def restaurent_like_update():
#     try:
#         u_id=get_jwt_identity()
#         print(u_id)
#         data=request.json
#         restaurent_id=data.get("restaurent_id")
#         cursor=g.db.cursor()
#         cursor.execute (f"SELECT * FROM `tbl_resturant_like` WHERE is_active=1 AND is_delete=0 AND user_id={u_id}")
#         user=cursor.fetchall() 
#         print(user)
#         if user:
#             g.db.commit()
#             cursor=g.db.cursor()
#             cursor.execute (f"UPDATE tbl_resturant_like SET is_active=0 , is_delete=1 WHERE user_id ='{u_id} AND resturant_id={restaurent_id}'")
#             g.db.commit()
#             return jsonify({'message':" Unlike successfully"}), 201 
#         else :
#             return jsonify({'Error':"unliked by user"}), 400 
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400
