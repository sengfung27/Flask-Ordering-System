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

UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager(app)
Bootstrap(app)
db = SQLAlchemy(app)
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"
))
from app import routes, models
from app.models import User, Role

# check for correctness
# me = db.session.query(User).filter_by(email="ms@example.com").first()
# print(me)
# if me is None:
#     print("nothing")
#
# role = me.role.role_type
# print(role)
# if role == "deliver":
#     print("we did it")

# create user
# user = User(email="delivery@example.com",role_id=5)
# user.set_password("1234")
# db.session.add(user)
# print(user)
# db.session.commit()
# me = db.session.query(User).filter_by(email="delivery@example.com").first()
# print(me)
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
# u = Testing(first='11', last='22')
# print(u)
# print (server.local_bind_port)
# db.session.add (u)
# db.session.commit()
# print("ok")

# delete id
# Testing.query.filter_by(id='2').delete()
# db.session.commit()
