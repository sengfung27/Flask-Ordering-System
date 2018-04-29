from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


# Set up user_loader
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.VARCHAR(255), unique=True, index=True)
    first_name = db.Column(db.VARCHAR(255))
    last_name = db.Column(db.VARCHAR(255))
    gender = db.Column(db.VARCHAR(6))
    address = db.Column(db.VARCHAR(255))
    password_hash = db.Column(db.VARCHAR(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), index=True)
    blacklist = db.Column(db.Boolean)
    number_of_warning = db.Column(db.Integer)
    rating = db.Column(db.DECIMAL(4, 2))
    payment = db.Column(db.VARCHAR(255))
    # payment = cardname + "," + cardnumber + "," + expired_month + "," + expired_year + "," + cvv
    # cardname, cardnumber, expired_month, expired_year, cvv = payment.split(',')
    role = db.relationship("Role", back_populates="user")
    # payment = db.relationship("Payment", back_populates="user")

    def set_role_id(self, rid):
        self.role_id = rid

    def get_role_id(self):
        return self.role_id

    def set_password(self, passwords):
        self.password_hash = generate_password_hash(passwords)

    def check_password(self, passwords):
        return check_password_hash(self.password_hash, passwords)

    def __repr__(self):
        return '<User: {}, {}>'.format(self.id, self.email)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.VARCHAR(60), unique=True)
    user = db.relationship("User", back_populates="role")  # user must equal to back_populates "user" on other table

    def __repr__(self):
        return '<Role: {}, {}>'.format(self.id)


class Cake(db.Model):
    __tablename__ = 'cakes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cake_name = db.Column(db.VARCHAR(255), nullable=False)
    category = db.Column(db.VARCHAR(255))
    visitor_price = db.Column(db.DECIMAL(5, 2))
    customer_price = db.Column(db.DECIMAL(5, 2))
    vip_price = db.Column(db.DECIMAL(5, 2))
    photo = db.Column(db.BLOB)
    description = db.Column(db.VARCHAR(255))
    rating = db.Column(db.DECIMAL(4, 2))

    def __repr__(self):
        return '<Cake: {}, {}, {}>'.format(self.id, self.cake_name, self.description)


# Vip only in one store 2 2
#                       1 3
#  deliver check registered customer ratng, when rating > 4, it will
#  automatically become vip
