from flask import Blueprint, request, jsonify, g, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import random
from flask_mail import Message, Mail
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from flask import Flask, redirect, url_for, render_template, request, flash

authentication_bp = Blueprint('auth', __name__)


@authentication_bp.route('/')
def sign_in():

    return render_template("sign_in.html")


@authentication_bp.route('/signuptemp')
def sign_up_temp():
    return render_template("log_in.html")

    return render_template("sign_in.html")


@authentication_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        try:
            data = request.form
            if not data:
                return jsonify({'message': 'data not found'}), 400
            email_id = data.get('Email')
            if not email_id:
                return jsonify({'message': 'email not found'}), 400
            user_password = data.get('user_password')
            if not user_password:
                return jsonify({'message': 'user_password not found'}), 400
            print(email_id, user_password)
            cursor = g.db.cursor()

            cursor.execute(
                f" SELECT * FROM tbl_user WHERE email = '{email_id}' and is_active=1 and is_delete=0 and is_verifyed=1 and user_type='ADMIN'")
            # cursor.execute(f" SELECT * FROM tbl_user WHERE email_id = '{email_id}'")
            user = cursor.fetchone()
            print(user)
            if user:
                is_password_correct = check_password_hash(
                    user[1], user_password)
                # print(user[6])
                # print(is_password_correct)
                if is_password_correct:
                    access_token = create_access_token(identity=user[0])

                    return jsonify({
                        'user': {
                            'access_token': access_token,
                            'email_id': email_id,
                            'id': user[0]
                        }
                    })
                else:
                    return jsonify({'error': 'Invalid password'}), 400
            else:
                return jsonify({'error': 'Invalid mobile/email or password'}), 400
        except Exception as e:
            return jsonify({'message': f'{e}'}), 400
    return render_template("welcome.html")


@authentication_bp.post('/sign-up')
def sign_up():
    try:
        data = request.json
        user_type = data.get("user_type")
        email = data.get('email')
        user_password = data.get('user_password')
        number = data.get('number')
        f_name = data.get('f_name')
        l_name = data.get('l_name')
        address = data.get("address")
        company_name = data.get("compny_name")
        profile_picture = data.get("profile_picture")
        dob = data.get("dob")
        title = data.get("title")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        if not data:
            return jsonify({'error': 'Do sign-up with all required data'}), 400
        elif not user_type:
            return jsonify({'error': 'Do sign-up with valid user_type'}), 400
        elif not email:
            return jsonify({'error': 'Do sign-up with valid email'}), 400
        elif not number:
            return jsonify({'error': 'Do sign-up with valid number'}), 400

        elif not user_password:
            return jsonify({'error': 'Do sign-up with valid user_password'}), 400
        elif not latitude:
            return jsonify({'error': 'Do sign-up with valid latitude'}), 400
        elif not longitude:
            return jsonify({'error': 'Do sign-up with valid longitude'}), 400

        cursor = g.db.cursor(dictionary=True)
        cursor.execute(
            f" SELECT * FROM tbl_user WHERE is_active=1 and is_delete=0 and email = '{email}' ")
        user = cursor.fetchall()
        print("---------------------------------->",user[0]['email'])
        if user:
            if user[0]['email'] == email:
                return jsonify({'message': 'User already registered with this email address'})

        password_hash = generate_password_hash(
            user_password, method='scrypt', salt_length=8)
        if user_type in ("CUSTOMER", "ADMIN"):
            cursor.execute(
                f"INSERT INTO tbl_user(f_name, l_name, user_type, email, user_password, profile_picture, latitude, "
                f"longitude, address, dob, number) VALUES ('{f_name}','{l_name}','{user_type}','{email}','{password_hash}', "
                f"'{profile_picture}','{latitude}','{longitude}','{address}','{dob}','{number}')")
        elif user_type == "MERCHANT":
            cursor.execute(
                f"INSERT INTO tbl_user(company_name, user_type, email, user_password, profile_picture, latitude, "
                f"longitude, address, title, number) VALUES ('{company_name}','{user_type}','{email}','{password_hash}',"
                f"'{profile_picture}','{latitude}','{longitude}','{address}','{title}','{number}')")
        cursor.execute(
            f" SELECT * FROM tbl_user WHERE email = '{email}'and is_active=1 and is_delete=0")
        new_user = cursor.fetchall()
        g.db.commit()
        send_email(new_user)
        return jsonify(
            {'message': f"User registered successfully,Please verify before login."}), 201

    except Exception as e:
        return jsonify({'error': f'{e}'})
        # return jsonify({'error': 'Do sign-up with all required details'}), 400


def send_email(new_user):
    from project import mail
    otp = random.randint(1001, 9999)
    print(otp)

    mail_id = new_user[0]['email']
    print(mail_id)
    if new_user:
        # msg = Message("Verification email", mailto:sender="itsramanuj77@gmail.com", recipients=[mail_id])
        msg = Message("Verification email",
                      sender="itsramanuj77@gmail.com", recipients=[mail_id])
        otp = random.randint(1001, 9999)
        msg.body = f"{otp} is your OTP for user verification."
        mail.send(msg)
    cursor = g.db.cursor()
    print("new user id", new_user[0]['id'])
    cursor.execute(
        f"INSERT INTO tbl_otp(user_id, otp) VALUES ('{new_user[0]['id']}','{otp}')")
    g.db.commit()


@authentication_bp.post('/verify-user/<id>')
def verify_user(id):
    user_id = id
    print("user_id", user_id)
    cursor = g.db.cursor()
    cursor.execute(
        f"SELECT * FROM tbl_user WHERE is_active=1 and is_delete=0 and id = '{user_id}'")
    user = cursor.fetchone()
    if not user:
        return jsonify({'message': 'No such user found'}), 400
    elif user[22] == 1:
        return jsonify({'message': 'User already verified'}), 200
    else:
        try:
            data = request.json
            entered_otp = data.get('otp')
            if not entered_otp:
                return jsonify({'message': 'Please Enter OTP'})
            else:
                cursor = g.db.cursor()
                cursor.execute(
                    f"SELECT otp FROM tbl_otp WHERE is_active=1 and is_delete=0 and user_id = '{user_id}'")
                otp_data = cursor.fetchone()

                if otp_data[0] == entered_otp:
                    print("verified")
                    print("otp data", otp_data)
                    cursor.execute(
                        f"UPDATE tbl_otp SET is_active = 0, is_delete = 1 WHERE user_id='{user_id}'")
                    cursor.execute(
                        f"UPDATE tbl_user SET is_verifyed = 1 WHERE id='{user_id}'")
                    g.db.commit()
                    return jsonify({'message': f"User verified successfully"})
                else:
                    return jsonify({'message': 'Entered OTP does not matched, Please Enter Valid OTP.'})

        except Exception as e:
            return jsonify({'error': f'{e}'})
            # return jsonify({'error': f'Please Enter OTP'})


@authentication_bp.post('/login')
def login():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'data not found'}), 400
        email_id = data.get('email')
        if not email_id:
            return jsonify({'message': 'email not found'}), 400
        user_password = data.get('  ')
        if not user_password:
            return jsonify({'message': 'user_password not found'}), 400
        print(email_id, user_password)
        cursor = g.db.cursor()

        cursor.execute(
            f" SELECT * FROM tbl_user WHERE email = '{email_id}' and is_active=1 and is_delete=0 and is_verifyed=1")
        # cursor.execute(f" SELECT * FROM tbl_user WHERE email_id = '{email_id}'")
        user = cursor.fetchone()
        print(user)
        if user:
            is_password_correct = check_password_hash(user[1], user_password)
            # print(user[6])
            # print(is_password_correct)
            if is_password_correct:
                access_token = create_access_token(identity=user[0])

                return jsonify({
                    'user': {
                        'access_token': access_token,
                        'email_id': email_id,
                        'id': user[0]
                    }
                })
            else:
                return jsonify({'error': 'Invalid password'}), 400
        else:
            return jsonify({'error': 'Invalid mobile/email or password'}), 400
    except Exception as e:
        return jsonify({'message': f'{e}'}), 400


@authentication_bp.get('/forgot_pwd')
def forgot_pwd():
    try:
        data = request.json
        email = data.get("email")
        if not email:
            return jsonify({'error': 'email is required'}), 404
        cursor = g.db.cursor()
        cursor.execute(
            f"select * from tbl_user where email='{email}' and is_active=1 and is_delete=0 and is_verifyed=1")
        user = cursor.fetchone()
        if user:
            print(user[2])
            from project import mail
            exp_time = datetime.now() + timedelta(minutes=10)
            # print(exp_time.timestamp())
            cursor.execute(
                f"UPDATE tbl_user SET forgot_exp={round(exp_time.timestamp())} where id={user[0]}")
            g.db.commit()
            hash_id = generate_password_hash(
                str(user[0]), method='scrypt', salt_length=8)
            msg = Message(
                'Hello', sender='mailto:itsramanuj77@gmail.com', recipients=[email])
            msg.body = f"click here to reset your password http://127.0.0.1:8000/reset_pwd/{hash_id}/{user[0]}"
            mail.send(msg)
            print(f"{hash_id}/{user[0]}")
            return jsonify({"message": "Email Send Successfully"}), 200
        return jsonify({"error": "Enter valid Email"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@authentication_bp.post('/reset_pwd/<hash_id>/<user_id>')
def reset_pwd(hash_id, user_id):
    try:
        is_id = check_password_hash(hash_id, user_id)
        if is_id:
            cursor = g.db.cursor()
            cursor.execute(
                f"select user_password,forgot_exp from tbl_user where id={user_id} and is_active=1 and is_delete=0 "
                f"and is_verifyed=1")
            user = cursor.fetchone()
            if user:
                if user[1] is not None:
                    current_time = round(datetime.now().timestamp())
                    if user[1] > current_time:
                        new_pwd = request.json.get('new_password')
                        if not new_pwd:
                            return jsonify({"error": "new password is required"}), 404
                        is_same_pwd = check_password_hash(user[0], new_pwd)
                        if not is_same_pwd:
                            hash_pwd = generate_password_hash(
                                new_pwd, method='sha256', salt_length=8)
                            cursor.execute(
                                f"update tbl_user set user_password='{hash_pwd}', forgot_exp=Null where id={user_id}")
                            g.db.commit()
                            return jsonify({"message": "password updated successfully"}), 200
                        return jsonify({"error": "Your old and new password is same"}), 400
                    return jsonify({'error': 'your time is expired'}), 400
                return jsonify({"error": "user not requested for new password"}), 400
            return jsonify({"error": "user not found"}), 404
        return jsonify({"error": "Worng user id or hash_id"}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@authentication_bp.post('/change_password')
@jwt_required()
def change_password():
    try:
        data = request.json
        if not data:
            return jsonify({'message': 'data not found'}), 400
        user_id = get_jwt_identity()
        new_password = data.get('new_password')
        if not new_password:
            return jsonify({'message': 'new_password not found'}), 400
        confirm_password = data.get('confirm_password')
        if not confirm_password:
            return jsonify({'message': 'confirm_password not found'}), 400

        if new_password == confirm_password:
            cursor = g.db.cursor()
            cursor.execute("SELECT * FROM tbl_user WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                password_hash = generate_password_hash(
                    confirm_password, method='scrypt', salt_length=8)
                try:
                    query = "UPDATE tbl_user SET user_password = %s WHERE id = %s"
                    cursor.execute(query, (password_hash, user_id))
                    g.db.commit()
                    return jsonify({'message': 'password updated successfully'})
                except Exception as e:
                    return jsonify({'message': str(e)}), 400
            else:
                return jsonify({'message': 'user not found'}), 400
        else:
            return jsonify({'message': "password and confirm password don't match"}), 400
    except Exception as e:
        return jsonify({'message': str(e)}), 400
