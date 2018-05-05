from app import app, db, login_manager
from flask import render_template, flash, redirect, request, url_for, jsonify, send_from_directory, session
# from app.forms import EditProfileForm, LoginForm, RegistrationForm
from app.models import User, Cake, Cart
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
#from app.forms import LoginForm, RegistrationForm

from werkzeug.utils import secure_filename
import os
from base64 import b64encode
import base64

# UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/uploads'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask_login import LoginManager, current_user, login_user, logout_user


def write_file(data, filename):
    with open(filename, 'wb') as f:
        f.write(data)


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
            login_user(e)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if current_user.role_id == 7:
                    next_page = url_for('manager', id=current_user.id)
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


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/menu')
def menu():
    cakes = Cake.query.all()

    return render_template('menu.html', cakes=cakes)


########################################################################################################################
# Customer


@app.route('/customer/description/<id>', methods=['GET', 'POST'])
def description(id):
    cake = Cake.query.filter_by(id=id).first()

    if request.method == 'POST':
        cart = Cart.query.filter_by(user_id=current_user.id, cake_id=cake.id).one_or_none()
        if cart is None:
            temp = Cart(cake_id=cake.id, user_id=current_user.id, amount=request.values.get('amount'),
                        price=cake.customer_price, status="Not submitted")
            db.session.add(temp)
            db.session.commit()
            flash('Added to your cart')
            return redirect(url_for('cart'))
        elif int(request.values.get('amount')) <= 0:
            flash("Please enter the amount you want to purchase.")
        else:
            cart.amount = request.values.get('amount')
            db.session.commit()
            flash('Added to your cart')
            return redirect(url_for('cart'))
    return render_template('customers/description.html', cake=cake)


@app.route('/logout')
@login_required(1, 3, 4, 5, 6, 7)
def logout():
    flash("You logged out")
    logout_user()
    return redirect(url_for('index'))


@app.route('/registration', methods=['GET', 'POST'])
def registration():
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
        idPic = request.files['identification']

        if request.values.get('password') == request.values.get('password2'):
            address = request.values.get('address1') + " " + \
                      request.values.get('address2') + ", " + \
                      request.values.get('city').upper() + ", " + \
                      request.values.get('state') + " " + \
                      str(request.values.get('zip_code'))

            if idPic and allowed_file(idPic.filename):
                try:
                    employee = User(email=request.values.get('email'), address=address, role_id='1'
                                    , gender=request.values.get('gender'), first_name=request.values.get('firstname'),
                                    last_name=request.values.get('lastname'), id_photo=idPic.read())
                    employee.set_password(request.values.get('password'))
                    db.session.add(employee)
                    db.session.commit()

                    flash('You have successfully registered! You may now login.')

                    return redirect(url_for('login'))
                except:
                    flash("There is an Error on register")
            else:
                flash("invalid file")
        else:
            flash('The specified passwords do not match')

    return render_template('customers/registerform.html')  # , form=form


@app.route('/checkout')
def checkout():
    user = User.query.filter_by(id=current_user.id).first()
    cardname, cardnumber, expired_month, expired_year, cvv = user.payment.split(',')
    return render_template('customers/checkout.html', user=user, cardname=cardname, cardnumber=cardnumber,
                           expired_month=expired_month, expired_year=expired_year, cvv=cvv)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    total = 0
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id)
        for i in cart:
            total += i.price * i.amount
    else:
        cart = ""
    return render_template('customers/cart.html', cart=cart, total=total)


@app.route('/edit_cart', methods=['GET', 'POST'])
def edit_cart():
    total = 0
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id)

    if request.method == "POST":
        if request.form['action'] == "submit_submit":
            for i in cart:
                if request.values.get('amount' + str(i.cake.id)) == "":
                    i.amount = i.amount
                else:  # request.values.get('amount' + str(i.cake.id)) != i.amount
                    i.amount = request.values.get('amount' + str(i.cake.id))
        else:  # submit_drop
            cake_id = request.form['action']
            cake_in_cart = Cart.query.filter_by(cake_id=cake_id).first()
            if cake_in_cart is not None:
                db.session.delete(cake_in_cart)
        db.session.commit()
        flash("Successful edit your cart")
    return render_template('customers/edit_cart.html', cart=cart)


@app.route('/customer/customer_profile/<id>')
@login_required(1, 3, 4)
def customer_profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('customers/customer_profile.html', user=user)


@app.route('/customer/customer_edit/<id>', methods=['GET', 'POST'])
@login_required(1, 3, 4)
def customer_edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == "POST":
        email = request.form.get('new_email')
        phone_number = request.form.get('new_phone_number')
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        new_cardname = request.form.get('cardname')
        new_cardnumber = request.form.get('cardnumber')
        new_expired_month = request.form.get('expmonth')
        new_expired_year = request.form.get('expyear')
        new_cvv = request.form.get('cvv')
        try:
            if email != "":
                user.email = email
            if address != "":
                user.address = address
            if password != "" and confirm_password != "":
                if password == confirm_password:
                    user.set_password(password)
            if new_cardname != "" and new_cardnumber != "" and new_expired_month != "" \
                    and new_expired_year != "" and new_cvv != "":
                if user.payment is not None:
                    card_name, card_number, expired_month, expired_year, cvv = user.payment.split(',')
                    if new_cardname != "":
                        card_name = new_cardname
                    if new_cardnumber != "":
                        card_number = new_cardnumber
                    if new_expired_month != "":
                        expired_month = new_expired_month
                    if new_expired_year != "":
                        expired_year = new_expired_year
                    if new_cvv != "":
                        cvv = new_cvv
                else:
                    card_name = new_cardname
                    card_number = new_cardnumber
                    expired_month = new_expired_month
                    expired_year = new_expired_year
                    cvv = new_cvv
                payment = card_name + "," + card_number + "," + expired_month + "," + expired_year + "," + cvv
                user.payment = payment
            db.session.commit()
            flash('You have successfully edit your profile!')
            return redirect(url_for('customer_profile', id=current_user.id))
        except:
            flash("Either your information is duplicated in our system or your password is wrong")
    return render_template('customers/customer_edit.html', user=user)


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
        cakePic = request.files['cakePic']

        if cakePic and allowed_file(cakePic.filename):
            filename = secure_filename(cakePic.filename)
            cakePic.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            customerPirce = 0.95 * float(request.values.get('price'))
            vipPrice = 0.9 * float(request.values.get('price'))

            newCake = Cake(cake_name=request.values.get('cakeName'), category=request.values.get('category'),
                           visitor_price=request.values.get('price'), customer_price=customerPirce, vip_price=vipPrice,
                           photo=filename, description=request.values.get('description'))

            db.session.add(newCake)
            db.session.commit()

            flash('success')
        else:
            flash('invalid file')
    return render_template('cooks/cookadditem.html', title='Cook')


@app.route('/cook/cook_profile/<id>')
@login_required(6)
def cook_profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('cooks/cook_profile.html', user=user)


@app.route('/cook/cook_edit/<id>', methods=['GET', 'POST'])
@login_required(6)
def cook_edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == "POST":
        email = request.form.get('new_email')
        phone_number = request.form.get('new_phone_number')
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
            if phone_number != "":
                user.phone_number = phone_number
            if address != "":
                user.address = address
            if password != "" and confirm_password != "":
                if password == confirm_password:
                    user.set_password(password)
            db.session.commit()
            flash('You have successfully edit your profile!')
            return redirect(url_for('cook_profile', id=current_user.id))
        except:
            flash("Either your information is duplicated in our system or your password is different")
    return render_template('cooks/cook_edit.html', user=user)


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


@app.route('/deliver/profile/<id>')
@login_required(5)
def delivery_profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('deliveries/profile.html', user=user)


@app.route('/deliver/edit/<id>', methods=['GET', 'POST'])
@login_required(5)
def deliver_edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == "POST":
        email = request.form.get('new_email')
        phone_number = request.form.get('new_phone_number')
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
            if phone_number != "":
                user.phone_number = phone_number
            if address != "":
                user.address = address
            if password != "" and confirm_password != "":
                if password == confirm_password:
                    user.set_password(password)
            db.session.commit()
            flash('You have successfully edit your profile!')
            return redirect(url_for('delivery_profile', id=current_user.id))
        except:
            flash("Either your information is duplicated in our system or your password is different")
    return render_template('deliveries/deliver_edit.html', user=user)


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


@app.route('/manager/<id>')
@login_required(7)
def manager(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('managers/manager.html', user=user)


@app.route('/manager/edit/<id>', methods=['GET', 'POST'])
@login_required(7)
def manager_edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == "POST":
        email = request.form.get('new_email')
        phone_number = request.form.get('new_phone_number')
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
            if phone_number != "":
                user.phone_number = phone_number
            if address != "":
                user.address = address
            if password != "" and confirm_password != "":
                if password == confirm_password:
                    user.set_password(password)
            db.session.commit()
            flash('You have successfully edit your profile!')
            return redirect(url_for('manager', id=current_user.id))
        except:
            flash("Either your information is duplicated in our system or your password is different")
    return render_template('managers/manager_edit.html', user=user)


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

########################################################################################################################
# Map

@app.route('/')
@app.route('/mapforcustomers')
def mapforcust():
    return render_template('/MapForCustomer.html')

@app.route('/mapforcustomers/ajax', methods=['POST'])
def mapforcoord():
    x = request.form.get('x', 0, type=int)
    y = request.form.get('y', 0, type=int)
    c_x = request.form.get('c_x', 0, type=int)
    c_y = request.form.get('c_y', 0, type=int)
    # x,y --> store -> products model
    return jsonify('success')


@app.route('/mapfordelivery')
@login_required(5)
def mapfordeli():
    return render_template('/MapForDelivery.html')