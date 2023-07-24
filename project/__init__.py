from flask import Flask, g
from flask_jwt_extended import JWTManager
from .authentication import authentication_bp
from .Restaurant import Restaurants_bp
from .user import user_bp
from .Restaurant_aboutus import resraurant_aboutus_bp
from .contact_us import contact_bp
from .staticdata import static_bp
import os
import mysql.connector
from flask_mail import Mail



app = Flask(__name__)



# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME='itsramanuj77@gmail.com',
#     MAIL_PASSWORD='pbghtvvkxesazezi'
# )

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mailto:itsramanuj77@gmail.com'
app.config['MAIL_PASSWORD'] = 'pbghtvvkxesazezi'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True


jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = os.environ['SECRET_KEY']
mail = Mail(app)

@app.before_request
def before_request():
    # g.mail = Mail(app)

    g.db = mysql.connector.connect(
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASSWORD'],
        host=os.environ['MYSQL_HOST'],
        database=os.environ['MYSQL_DB'],
        # port=os.environ['MYSQL_PORT']
        # JWT_SECRET_KEY=os.environ['JWT_SECRET_KEY']

    )


@app.after_request
def after_request(response):
    g.db.close()
    return response


app.register_blueprint(authentication_bp)

# app.register_blueprint(user_bp)
# app.register_blueprint(hospital_bp)
# app.register_blueprint(product_bp)

app.register_blueprint(user_bp)
app.register_blueprint(Restaurants_bp)
app.register_blueprint(resraurant_aboutus_bp)
app.register_blueprint(contact_bp)
app.register_blueprint(static_bp)
