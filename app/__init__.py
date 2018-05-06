from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from sshtunnel import SSHTunnelForwarder
from flask_login import LoginManager
from sqlalchemy import create_engine, func, or_
from flask_bootstrap import Bootstrap

app = Flask(__name__)
server = SSHTunnelForwarder(
    ('134.74.126.104', 22),  # 104
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
app.secret_key = 'super secret key'
from app import routes, models, errors
from app.models import User, Role, Cake, Cart
from datetime import datetime



# user = User(email="manager@example.com", role_id=7, first_name="mana",last_name="ger",gender="male",
# store_id=1, order_made=0, rating=0.0)
# user = User(email="customer@example.com", role_id=3, first_name="mana",last_name="ger",gender="male",
# store_id=1, order_made=0, rating=0.0,blacklist=0)
#
# user.set_password('1234')
# db.session.add(user)
# db.session.commit()
# i = Cart.query.filter(or_(Cart.user_id==31,Cart.cake_id==11, Cart.status=="In Process"))
# for j in i:
#     print(j.user_id, j.cake_id, j.status)
# i = Cart.index
# print(i)
# Cart.index += 1
# print(i, Cart.index)
# o = db.session.query(func.max(Cart.id)).scalar()

# print(o)
# cart_user = Cart.query.func.count(user_id=31, status="In process")
# if cart_user > 1:
#     print("yeah")
# else:
#     print("No")
# current_user.last_seen = datetime.utcnow()
# w = "wqewe,qew,qewe"
# str1 = w.split(',')
# print(str1)
# p = ','.join(str1)
# print(p)
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

# user = User(email="delivery@example.com",role_id=5,first_name="delivery",last_name="man",gender="male")
# user.set_password("1234")
# db.session.add(user)
# print(user)
# db.session.commit()
# print(user)
# me = db.session.query(User).filter_by(email="delivery@example.com",last_name="n").first()
# print(me)
# print(me.role_id)
# print(me.role.role_type)
# me = db.session.query(Role).filter_by(role_type="deliver").first()
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
