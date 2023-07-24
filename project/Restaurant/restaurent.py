import os
from flask import Blueprint, app,request,jsonify,g,flash,json
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from datetime import timedelta
from flask_mysql_connector import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash



Restaurants_bp= Blueprint('Restaurants',__name__)
blacklist=set()


@Restaurants_bp.get('/Restaurant_hedar')
@jwt_required()
def hospital_hedar():
    try:
        u_id=get_jwt_identity()
        cursor=g.db.cursor(dictionary=True)
        cursor.execute('SELECT l_name FROM tbl_user WHERE is_active= 1 AND is_delete=0 AND is_verifyed=1 AND id=%s',(u_id,))
        user=cursor.fetchone()
        if not user:
            return jsonify({"Error":"user not found"}),400
        import time    
        import datetime
        currentTime = time.strftime('%H:%M') 
        currentTime = datetime.datetime.now()
        if 6 <= currentTime.hour < 12 :
            time_u=('Good morning')
        elif 12 <= currentTime.hour < 16:
            time_u=('Good afternoon')
        else:
            time_u=('Good evening')
        if user:
            return jsonify({u_id:user},{"Message":time_u}),200
    except Exception as e:
        return jsonify({"Error": str(e) }),400
    


@Restaurants_bp.get('/Restaurant_search/<places>')
@jwt_required()
def Restaurant_search(places):
    try:
        i=(int(places))
        search=request.json.get("search")
        if i == 1:
            if search=="":
                return  jsonify({'Error':"search plz"}), 400
            cursor=g.db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM tbl_user WHERE address LIKE '%{search}%' AND user_type='MERCHANT'")
            user=cursor.fetchall()
            if user: 
                return  jsonify({'message':user}), 201
            return  jsonify({'Error':"data not found"}),401            
        elif i==2:
            if search=="":
                return  jsonify({'Error':"search plz"}), 400
            cursor=g.db.cursor(dictionary=True)
            cursor.execute(f"SELECT * FROM tbl_user WHERE f_name LIKE '%{search}%' AND  is_active= 1 AND is_delete=0 AND is_verifyed = 1")
            user=cursor.fetchall()
            if user: 
                return  jsonify({'message':user}), 201
            return  jsonify({'Error':"data not found"}),401
        return  jsonify({'Error':"Cheack url"}),401   
    except Exception as e:
        return jsonify({"Error": str(e) }),400
    


@Restaurants_bp.get('/Display_New_Restaurants')
@jwt_required()
def Display_New_Restaurants():
    try:
        #u_id=get_jwt_identity()
        cursor=g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT tbl_user.id,tbl_rating.merchant_id,tbl_user.company_name,tbl_user.profile_picture,tbl_user.title,tbl_user.avg_rating,tbl_rating.comments,tbl_rating.created_t FROM tbl_user LEFT JOIN tbl_rating ON tbl_rating.merchant_id=tbl_user.id WHERE tbl_user.user_type='MERCHANT' ORDER BY tbl_user.id DESC")
        user=cursor.fetchall()   
        return  jsonify({'message':user}), 201
    except Exception as e:
        return jsonify({"Error": str(e) }),400    
    

   
    
@Restaurants_bp.get('/Restaurants_most_raaved')
@jwt_required()
def Restaurants_most_raaved():
    try:
        cursor=g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT tbl_user.id,COUNT(tbl_rating.merchant_id),tbl_user.company_name,tbl_user.profile_picture,tbl_user.title,tbl_user.avg_rating,tbl_rating.comments,tbl_rating.created_t FROM tbl_user JOIN tbl_rating ON tbl_rating.merchant_id=tbl_user.id WHERE tbl_user.user_type='MERCHANT' ORDER BY COUNT(tbl_rating.merchant_id) DESC;")
        user=cursor.fetchall()   
        return  jsonify({'message':user}), 201
    except Exception as e:
        return jsonify({"Error": str(e) }),400    
    
@Restaurants_bp.get('/Like/<user_id_2>')
@jwt_required()
def Like(user_id_2):
    u=int(user_id_2)
    u_id=get_jwt_identity()
    cursor=g.db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM tbl_user WHERE id={u} and user_type='MERCHANT'")
    user=cursor.fetchone()
    if user:
        cursor=g.db.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM tbl_like WHERE user_id_1={u_id}  and user_id_2={u}")
        user=cursor.fetchone()
        if not user:
            cursor=g.db.cursor()
            cursor.execute (f"INSERT INTO tbl_like(user_id_1,user_id_2) VALUES ({u_id},{u})")
            g.db.commit()
            return  jsonify({'message':"Like successfull inserted"}), 201
        return  jsonify({'Error':"user liked already in this post"}),401
    return  jsonify({'message':"post is not available"}), 400

       
   


#    SELECT tbl_user.compny_name,tbl_user.coumpny_profile_pitcuher,tbl_user.title,tbl_user.avg_rating,tbl_rating.comments,tbl_rating.likes,tbl_rating.created_t FROM tbl_user JOIN tbl_rating ON tbl_rating.merchant_id=tbl_user.id WHERE tbl_user.user_type="MERCHANT";



# SELECT tbl_user.compny_name,tbl_user.coumpny_profile_pitcuher,tbl_user.title,tbl_user.avg_rating,tbl_rating.comments,tbl_rating.likes,tbl_rating.created_t FROM tbl_user JOIN tbl_rating ON tbl_rating.merchant_id=tbl_user.id WHERE tbl_user.user_type='MERCHANT' ORDER BY tbl_user.avg_rating DESC




# @hospital_bp.get('/Nearby_hospital')
# @jwt_required()
# def Nearby_hospital():
#     try:
#         u_id=get_jwt_identity()
#         if u_id:
#             cursor=g.db.cursor()
#             cursor.execute(f"SELECT * FROM tbl_user_address WHERE  user_id ={u_id}")
#             user1=cursor.fetchone()  
#             cursor=g.db.cursor(dictionary=True)
#             cursor.execute (f"SELECT tr.name,tr.clinic_img,tr.location,tr.clinic_type,tr.avg_rating ,round(6371 * acos(cos(radians({user1[3]})) * cos(radians(tr.latitude))* cos(radians({user1[4]}) - radians(tr.longitude)) + sin(radians({user1[3]})) * sin(radians(tr.latitude)))) as Distance FROM tbl_clinic tr GROUP BY tr.id HAVING Distance<=15 ORDER BY avg_rating DESC")
#             user=cursor.fetchall()   
#             return user
#         return jsonify({'Error':"user not found"}), 401
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400
    



# @hospital_bp.get('/Nearby_hospital/<id>')
# @jwt_required()
# def Nearby_hospital(id):
#     try:
#         u_id=get_jwt_identity()
#         if u_id:
#             cursor=g.db.cursor()
#             cursor.execute(f"SELECT * FROM tbl_clinic WHERE is_active=1 and is_delete=0 and id={id}")
#             user1=cursor.fetchone()  
#             if user1:
#                 cursor=g.db.cursor(dictionary=True)
#                 cursor.execute (f"SELECT tbl_doctor.id,tbl_clinic.name,tbl_clinic.clinic_img,tbl_doctor.specialization,tbl_doctor.start_time,tbl_doctor.end_time,tbl_user.user_img ,tbl_user.f_name,tbl_user.l_name FROM `tbl_doctor` JOIN tbl_clinic ON tbl_doctor.clinic_id=tbl_clinic.id JOIN tbl_user ON tbl_doctor.user_id=tbl_user.id WHERE clinic_id={id}")
#                 user=cursor.fetchall()   
#                 return user
#             return jsonify({'Error':"hospital not found"}), 401
#         return jsonify({'Error':"user not found"}), 401
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400
    
    


 
    



# @resraurant_bp.get('/top_picks')
# @jwt_required()
# def top_picks():
#     try:
#         cursor=g.db.cursor(dictionary=True)
#         cursor.execute(f"SELECT food_image,food_name,food_price FROM `tbl_food` ORDER BY total_likes DESC LIMIT 5")
#         user=cursor.fetchall()   
#         return  jsonify({'message':user}), 201  
#     except Exception as e:
#         return jsonify({"Error": str(e) }),400
 
    

    


           

