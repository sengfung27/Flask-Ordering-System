from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from flask_login import LoginManager
from sqlalchemy import create_engine
from flask_bootstrap import Bootstrap

app = Flask(__name__)
server = SSHTunnelForwarder(
    ('134.74.126.104', 22),
    ssh_username='huan2077',
    ssh_password='23242077',
    remote_bind_address=('134.74.146.21', 3306))
server.start()
engine = create_engine('mysql+pymysql://F17336Pwhuang:23242077@127.0.0.1:%s/F17336Pwhuang' % server.local_bind_port)
app.config[
    'SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://F17336Pwhuang:23242077@127.0.0.1:%s/F17336Pwhuang' % server.local_bind_port
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/uploads'

login_manager = LoginManager(app)
Bootstrap(app)
db = SQLAlchemy(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
# UPLOAD_FOLDER = '/Users/James/Desktop/Flask-Ordering-System/app/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from app import routes, models, errors
from app.models import User, Role, Cake, Cart

# myString = "wtf ,this ,so "
# me, tre, qw = myString.split(",")
# print(me)
# print(tre)
# print(qw)
# me = User.query.filter_by(email="ii@example.com")
# print(me)
# if me is None:
#     print("nothing")
# for i in me:
#     print("User {} {}".format(i.email, i.first_name))
# User.update().va
# db.session.update()


# create user
# user = User(email="customer@example.com",role_id=3,first_name="m",last_name="n",gender="male")
# user.set_password("1234")
# db.session.add(user)
# print(user)
# db.session.commit()
# print(user)
# me = db.session.query(User).filter_by(email="customer@example.com",last_name="n").first()
# print(me)
# print(me.role_id)
# print(me.role.role_type)
# me = db.session.query(Role).filter_by(role_type="customer").first()
# print(me)
# print(me.role_type)
# print(me.user.email)

# foreign key access
# if more than one
# c =  Cart.query.filter_by(user_id=31)
# for me in c:
#     print(me)
#     print(me.amount)
#     print(me.cake.cake_name)
#     print(me.user.email)

# only one
# c =  Cart.query.filter_by(user_id=31).first()
# loop
# users = User.query.all()
#
# for u in users:
#     print(u.id, u.username)

# query.all
# users = Testing.query.all()
# for row in users:
#     print("id", str(row.id))
# our_user = db.session.query(Testing).filter_by(id='3').first()
# if our_user.id == 3:
#     print("we did it")
# else:
#     print("wtf")


# add id
# u = Cake(cake_name="cheese cake", description='yummy')
# print(u)
# db.session.add(u)
# db.session.commit()
# print("ok")

# delete id
# Testing.query.filter_by(id='2').delete()
# db.session.commit()

# Session
# if 'username' in session:
#       username = session['username']
#       session['whateve'] = pas
#       session.pop('username', None)


# from datetime import date
# today = date.today()

# request.form['action'] == "submit_submit"
# request.values.get('asds')
