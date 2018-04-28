from app import app, db, login_manager
from flask import render_template, flash, redirect, request, url_for, jsonify, send_from_directory
# from app.forms import EditProfileForm, LoginForm, RegistrationForm
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm

from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/static'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask_login import LoginManager, current_user, login_user, logout_user

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
        if current_user.role_id == 7:
            return redirect(url_for('manager'))
        if current_user.role_id == 6:
            return redirect(url_for('cook'))
        if current_user.role_id == 5:
            return redirect(url_for('delivery'))
        else:
            return redirect(url_for('index'))
    if request.method == 'POST':
        e = User.query.filter_by(email=request.values.get('email')).first()
        if e is not None and e.check_password(request.values.get('password')):
            login_user(e, remember=request.values.get('remember_me'))
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if current_user.role_id == 7:
                    next_page = url_for('manager')
                elif current_user.role_id == 6:
                    next_page = url_for('cook')
                elif current_user.role_id == 5:
                    next_page = url_for('delivery')
                else:
                    next_page = url_for('index')
            return redirect(next_page)
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
@login_required(1, 3, 4, 5, 6, 7)
def logout():
    flash("You logged out")
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        if request.values.get('password') == request.values.get('password2'):
            address = request.values.get('address1') + " " + \
                      request.values.get('address2') + ", " + \
                      request.values.get('city').upper() + ", " + \
                      request.values.get('state') + " " + \
                      str(request.values.get('zip_code'))
            try:
                employee = User(email=request.values.get('email'), address=address, role_id='1'
                                , gender=request.values.get('gender'), first_name=request.values.get('firstname'),
                                last_name=request.values.get('lastname'))
                employee.set_password(request.values.get('password'))
                db.session.add(employee)
                db.session.commit()

                flash('You have successfully registered! You may now login.')

                return redirect(url_for('login'))
            except:
                flash("There is an Error on register")
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
@login_required(1, 3, 4)
def customer_profile():
    return render_template('customers/customer_profile.html', title='Menu')


@app.route('/customer/order_history')
@login_required(1, 3, 4)
def order_history():
    return render_template('customers/order_history.html', title='Menu')


@app.route('/customer/rating')
@login_required(1, 3, 4)
def rating():
    return render_template('customers/rating.html', title='Menu')


########################################################################################################################
# Cook


@app.route('/cook')
@login_required(6)
def cook():
    return render_template('cooks/cook.html', title='Cook')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/cook/additem', methods=['GET', 'POST'])
@login_required(6)
def additem():
    if request.method == 'POST':
        print(request.values.get('cakeName'))
        print(request.values.get('category'))
        print(request.values.get('price'))
        print(request.values.get('description'))

        file = request.files['cakePic']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            flash('success')

            return redirect(url_for('additem'))
        else:
            flash('not valid file')

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


@app.route('/delivery/notification')
@login_required(5)
def delivery_notification():
    return render_template('deliveries/notification.html', title='Delivery')


########################################################################################################################
# Manager


@app.route('/manager')
@login_required(7)
def manager():
    return render_template('managers/manager.html', title='Manager')


@app.route('/manager/CookWarning')
@login_required(7)
def cookwarning():
    return render_template('managers/CookWarning.html')


@app.route('/manager/CustomerApplication', methods=['GET', 'POST'])
@login_required(7)
def application():
    me = User.query.filter_by(role_id=1)
    if request.method == 'POST':
        for i in me:
            # visitor become customer, 1 to 3
            i.role_id = 3
            db.session.commit()
        flash("Success to update all visitor to customer")
    return render_template('managers/CustomerApplication.html', me=me)


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
