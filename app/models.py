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

    role = db.relationship("Role", back_populates="user")

    def set_role_id(self, rid):
        self.role_id = rid

    def get_role_id(self):
        return self.role_id

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User: {}, {}>'.format(self.id, self.email)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role_type = db.Column(db.VARCHAR(60), unique=True)

    user = db.relationship("User", back_populates="role")  # user must equal to back_populates "user" on other table

    def __repr__(self):
        return '<Role: {}, {}>'.format(self.id, self.role_type)

# class Testing(UserMixin, db.Model):
#     __tablename__ = 'testing'
#     id = Column(db.Integer, primary_key=True, autoincrement=True)
#     first = Column(db.Integer)
#     last = Column(db.Integer)
#
#     def __repr__(self):
#         return '<Testing: {}, {} {}>'.format(self.id, self.first, self.last)
