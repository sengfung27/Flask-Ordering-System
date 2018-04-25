from app import app, db, login_manager
from flask import render_template, flash, redirect, request, url_for, jsonify
# from app.forms import EditProfileForm, LoginForm, RegistrationForm
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm

from werkzeug.utils import secure_filename
import os
from flask import send_from_directory


UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm



def login_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login', next=request.url))
            urole = current_user.role_id
            boo = False
            for role in roles:
                if urole == role:
                    boo = True
            if not boo:
                return login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        e = User.query.filter_by(email=request.values.get('email')).first()
        if e is not None and e.check_password(request.values.get('password')):
            login_user(e, remember=request.values.get('remember_me'))
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password.')
    return render_template('login.html', title='Sign In')



@app.route('/menu')
def menu():
    return render_template('menu.html', title='Menu')


########################################################################################################################
# Customer


@app.route('/customer/description')
def description():
    return render_template('customers/description.html')


@app.route('/logout')
@login_required(3, 4, 5, 6, 7)
def logout():
    flash("You logged out")
    logout_user()
    return redirect(url_for('index'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return "success"
        else:
            return "not valid"
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'], ))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.values.get('password') != request.values.get('password2'):
            address = request.values.get('address1') + " " + \
                      request.values.get('address2') + ", " + \
                      request.values.get('city') + ", " + \
                      request.values.get('state') + " " + \
                      str(request.values.get('zip_code'))
            employee = User(email=request.values.get('email'), address=address, role_id='3'
                            , gender=request.values.get('gender'), first_name=request.values.get('firstname'),
                            last_name=request.values.get('lastname'))
            employee.set_password(request.values.get('password'))
            db.session.add(employee)
            db.session.commit()

            flash('You have successfully registered! You may now login.')

            return redirect(url_for('login'))
        else:
            flash('The specified passwords do not match')

    return render_template('customers/registerform.html')  # , form=form


@app.route('/signup')
def checkout():
    return render_template('customers/checkout.html', title='Menu')


@app.route('/confirmation')
def confirmation():
    return render_template('customers/confirmation.html', title='Menu')


@app.route('/customer/customer_profile')
@login_required(3, 4)
def customer_profile():
    return render_template('customers/customer_profile.html', title='Menu')


@app.route('/customer/order_history')
@login_required(3, 4)
def order_history():
    return render_template('customers/order_history.html', title='Menu')


@app.route('/customer/rating')
@login_required(3, 4)
def rating():
    return render_template('customers/rating.html', title='Menu')


########################################################################################################################
# Cook


@app.route('/cook')
@login_required(6)
def cook():
    return render_template('cooks/cook.html', title='Cook')


@app.route('/cook/additem')
@login_required(6)
def additem():
    return render_template('cooks/cookadditem.html', title='Cook')


@app.route('/cook/cook_profile')
@login_required(6)
def cook_profile():
    return render_template('cooks/cook_profile.html', title='Cook')


@app.route('/cook/dropped_notification')
@login_required(6)
def dropped_notification():
    return render_template('cooks/dropped_noti.html', title='Cook')


@app.route('/cook/warning_notification')
@login_required(6)
def warning_notification():
    return render_template('cooks/warning_noti.html', title='Cook')


########################################################################################################################
# Delivery

@app.route('/delivery')
@login_required(5)
def delivery():
    return render_template('deliveries/delivery.html', title='Delivery')


@app.route('/delivery/notification')
@login_required(5)
def notification():
    return render_template('deliveries/notification.html', title='Delivery')


@app.route('/delivery/profile')
@login_required(5)
def delivery_profile():
    return render_template('deliveries/profile.html', title='Delivery')


@app.route('/delivery/route')
@login_required(5)
def delivery_route():
    return render_template('deliveries/route.html', title='Delivery')


########################################################################################################################
# Manager


@app.route('/manager')
@login_required(7)
def manager():
    return render_template('managers/manager.html', title='Manager')


@app.route('/manager/CookWarning')
@login_required(7)
def CookWarning():
    return render_template('managers/CookWarning.html')


@app.route('/manager/CustomerApplication')
@login_required(7)
def application():
    return render_template('managers/CustomerApplication.html')


@app.route('/manager/CustomerComplaint')
@login_required(7)
def complaint():
    return render_template('managers/CustomerComplaint.html')


@app.route('/manager/DecideDelivery')
@login_required(7)
def decidedelivery():
    return render_template('managers/DecideDelivery.html')


@app.route('/manager/DeliverWarning')
@login_required(7)
def deliverwarning():
    return render_template('managers/DeliverWarning.html')


@app.route('/manager/ManageCustomers')
@login_required(7)
def managecustomers():
    return render_template('managers/ManageCustomers.html')


@app.route('/manager/PayWage')
@login_required(7)
def paywage():
    return render_template('managers/PayWage.html')
