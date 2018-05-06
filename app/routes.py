from app import app, db, login_manager
from flask import render_template, flash, redirect, request, url_for, jsonify, send_from_directory, session
# from app.forms import EditProfileForm, LoginForm, RegistrationForm
from app.models import User, Cake, Cart
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
# from app.forms import LoginForm, RegistrationForm
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from decimal import *
from sqlalchemy import func, or_

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
from base64 import b64encode
import base64

# UPLOAD_FOLDER = '/Users/caizhuoying/Documents/Flask-Ordering-System/app/uploads'
# ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from flask_login import LoginManager, current_user, login_user, logout_user

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


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
            return redirect(url_for('deliver'))
        else:
            return redirect(url_for('index'))
    if request.method == 'POST':
        e = User.query.filter_by(email=request.values.get('email')).first()
        if e is None:
            flash("Our system does not have your record. "
                  "Please check your Email or password. "
                  "Or create a new account.")
        elif e is not None and e.check_password(request.values.get('password')) \
                and (e.blacklist is None or e.blacklist == 0):
            login_user(e)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                if current_user.role_id == 7:
                    next_page = url_for('manager', id=current_user.id)
                elif current_user.role_id == 6:
                    next_page = url_for('cook')
                elif current_user.role_id == 5:
                    next_page = url_for('deliver')
                else:
                    next_page = url_for('index')
            return redirect(next_page)
        elif e.blacklist:
            flash("Blacklist account will be blocked")
        else:
            flash('Invalid email or password')
    return render_template('login.html', title='Sign In')


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/menu')
def menu():
    cakes = Cake.query.filter(Cake.cake_name != "Custom Cake")

    return render_template('menu.html', cakes=cakes)

@app.route('/customize_cake', methods=['GET', 'POST'])
def customize_cake():
    cooks = User.query.filter_by(role_id=6)  # store_id = ?
    if request.method == 'POST':
            description = request.values.get('cake flavors') + ", " + request.values.get('cake filling') + ", " + \
                          request.values.get('frosting') + ", " + request.values.get('toppings') + ", " +\
                          request.values.get('size')
            newCake = Cake(cake_name="Custom Cake",
                           visitor_price=120, customer_price=0.95*120, vip_price=0.9*120,
                           photo="CustomCake_Default.png", description=description)
            db.session.add(newCake)

            cake = Cake.query.filter_by(description=description).first()

            if current_user.is_anonymous:
                amount = int(request.values.get('amount'))
                if amount <= 0:
                    flash("Invalid amount, Please enter a positive amount")
                    return redirect(url_for('description', id=cake.id))
                cook_id = int(request.values.get('cook'))
                if str(cake.id) not in session:
                    cook = User.query.filter_by(id=cook_id).first()
                    session[str(cake.id)] = [cake.id, amount, cook.id, cake.cake_name,
                                             cook.first_name, cake.visitor_price]
                    flash("Successful store to Session")
                    return redirect(url_for('menu'))
                else:
                    flash("Initial amount: " + str(session[str(cake.id)][1]))
                    session[str(cake.id)][1] = amount
                    flash("After changed the amount: " + str(session[str(cake.id)][1]))
                    return redirect(url_for('menu'))

            else:  # if current_user.id
                cart = Cart.query.filter_by(user_id=current_user.id, cake_id=cake.id,
                                            status="Not submitted").one_or_none()
                cook = request.form['cook']

                amount = int(request.values.get('amount'))
                if amount <= 0:
                    flash("Invalid amount. Please enter a positive amount")
                    return redirect(url_for('description', id=cake.id))
                if cart is None:
                    temp = Cart(cake_id=cake.id, user_id=current_user.id, amount=1,
                                price=cake.customer_price, status="Not submitted", cook_id=cook, cake_rating=0,
                                deliver_rating=0, user_rating=0, store_rating=0)
                    db.session.add(temp)
                    db.session.commit()
                    flash('Added to your cart')
                    return redirect(url_for('cart'))

            flash('Added to your cart successfully')
    return render_template('customize_cake.html', cooks=cooks)


########################################################################################################################
# Customer


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
            if idPic and allowed_file(idPic.filename):
                filename = secure_filename(idPic.filename)
                path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                idPic.save(path)
                newname = request.values.get('email') + '.png'
                target = os.path.join(app.config['UPLOAD_FOLDER'], newname)
                os.rename(path, target)

                print(request.values.get('address1'))

                u = User.query.filter_by(first_name=request.values.get('firstname'),
                                         last_name=request.values.get('lastname'),
                                         address=request.values.get('address')).first()
                if u is None:
                    try:
                        employee = User(email=request.values.get('email'), address=request.values.get('address1'),
                                        role_id='1', gender=request.values.get('gender'),
                                        first_name=request.values.get('firstname'),
                                        last_name=request.values.get('lastname'), id_photo=newname, rating=0.0,
                                        store_id=1, number_of_warning=0, order_made=0, blacklist=0, number_of_drop=0)

                        employee.set_password(request.values.get('password'))
                        db.session.add(employee)
                        db.session.commit()

                        flash('You have successfully registered! You may now login.')

                        return redirect(url_for('login'))
                    except:
                        flash("Error in requesting, db down")
                elif u.blacklist == 1:
                    flash("You have been banned from our system")
                else:
                    flash("Provided information is duplicated in our system.")
            else:
                flash("invalid file")
        else:
            flash('The specified passwords do not match')

    return render_template('customers/registerform.html')  # , form=form


@app.route('/customer/description/<id>', methods=['GET', 'POST'])
def description(id):
    cake = Cake.query.filter_by(id=id).first()
    cooks = User.query.filter_by(role_id=6)  # store_id = ?
    if request.method == 'POST' and current_user.is_anonymous:
        amount = int(request.values.get('amount'))
        if amount <= 0:
            flash("Invalid amount")
            return redirect(url_for('description', id=cake.id))
        cook_id = int(request.values.get('cook'))
        if str(cake.id) not in session:
            cook = User.query.filter_by(id=cook_id).first()
            session[str(cake.id)] = [cake.id, amount, cook.id, cake.cake_name,
                                     cook.first_name, cake.visitor_price]
            flash("Successful store to Session")
            return redirect(url_for('menu'))
        else:
            flash("Initial amount: " + str(session[str(cake.id)][1]))
            session[str(cake.id)][1] = amount
            flash("After changed the amount: " + str(session[str(cake.id)][1]))
            return redirect(url_for('menu'))
    elif request.method == 'POST' and current_user.id:
        cart = Cart.query.filter_by(user_id=current_user.id, cake_id=cake.id, status="Not submitted").first()
        cook = request.form['cook']
        amount = int(request.values.get('amount'))
        if amount <= 0:
            flash("Invalid amount. Please enter a positive amount")
            return redirect(url_for('description', id=cake.id))
        if cart is None:
            temp = Cart(cake_id=cake.id, user_id=current_user.id, amount=amount,
                        price=cake.customer_price, status="Not submitted", cook_id=cook, cake_rating=0,
                        deliver_rating=0, user_rating=0, store_rating=0)
            db.session.add(temp)
            db.session.commit()
            flash('Added to your cart')
            return redirect(url_for('cart'))

        else:
            cart.amount = request.values.get('amount')
            db.session.commit()
            flash('Added to your cart')
            return redirect(url_for('cart'))
    return render_template('customers/description.html', cake=cake, cooks=cooks)


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    total = 0
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id, status="Not submitted")

        for i in cart:
            total += i.price * i.amount
        return render_template('customers/cart.html', cart=cart, total=total)
    else:
        cart_array = []
        total = 0
        cake_total = db.session.query(func.max(Cake.id)).scalar()
        for j in range(1, int(cake_total) + 1):
            if str(j) in session:
                i = str(j)
                temp = []
                cake_id = session[i][0]
                amount = session[i][1]
                cook_id = session[i][2]
                cake_name = session[i][3]
                cook_first_name = session[i][4]
                visitor_price = session[i][5]
                temp.append(cake_id)
                temp.append(amount)
                temp.append(cook_id)
                temp.append(cake_name)
                temp.append(cook_first_name)
                temp.append(visitor_price)
                cart_array.append(temp)
                total += amount * visitor_price
        return render_template('customers/cart.html', cart_array=cart_array, total=total)


@app.route('/edit_cart', methods=['GET', 'POST'])
def edit_cart():
    if current_user.is_authenticated:
        cart = Cart.query.filter_by(user_id=current_user.id, status="Not submitted")
        if request.method == "POST":
            if request.form['action'] == "submit_submit":
                for i in cart:
                    if request.values.get('amount' + str(i.cake.id)) != "":
                        amount = int(request.values.get('amount' + str(i.cake.id)))
                        if amount <= 0:
                            flash("Invalid amount. Please reenter a amount")
                            return redirect(url_for('edit_cart'))
                        i.amount = request.values.get('amount' + str(i.cake.id))
            else:  # submit_drop
                cake_id = request.form['action']
                cake_in_cart = Cart.query.filter_by(cake_id=cake_id, status="Not submitted").first()
                if cake_in_cart is not None:
                    db.session.delete(cake_in_cart)
            db.session.commit()
            flash("Successful edit your cart")
            return redirect(url_for('cart'))
        return render_template('customers/edit_cart.html', cart=cart)
    else:
        cart_array = []
        cake_total = db.session.query(func.max(Cake.id)).scalar()
        for j in range(1, int(cake_total) + 1):
            if str(j) in session:
                i = str(j)
                temp = []
                cake_id = session[i][0]
                amount = session[i][1]
                cake_name = session[i][3]
                temp.append(cake_id)
                temp.append(amount)
                temp.append(cake_name)
                cart_array.append(temp)
        if current_user.is_anonymous and request.method == "POST":
            if request.form['action'] == "submit_submit":
                for j in range(1, int(cake_total) + 1):
                    if str(j) in session:
                        i = str(j)
                        if request.values.get('amount' + str(session[i][1])) != "":
                            if int(request.values.get('amount' + str(session[i][0]))) <= 0:
                                flash("Invalid, please enter again")
                                return redirect(url_for('edit_cart'))
                            session[i][1] = int(request.values.get('amount' + str(session[i][0])))
                            flash("Successful updated one cake")
                        else:
                            flash("You must enter a number")
                flash("Successful updated the amount of cakes")
                return redirect(url_for('cart'))
            else:  # submit_drop
                cake_id = request.form['action']
                if str(cake_id) in session:
                    session.pop(str(cake_id), None)
                    flash("You cake has been dropped")
                    return redirect(url_for('cart'))
        return render_template('customers/edit_cart.html', cart_array=cart_array)


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if current_user.is_authenticated:
        user = User.query.filter_by(id=current_user.id).first()
        if user.payment is not None:
            cardname, cardnumber, expired_month, expired_year, cvv = user.payment.split(',')
            return render_template('customers/checkout.html', user=user, cardname=cardname, cardnumber=cardnumber,
                                   expired_month=expired_month, expired_year=expired_year, cvv=cvv,
                                   billing_address=user.billing_address)
        if request.method == 'POST':
            user = User.query.filter_by(id=current_user.id).first()
            index = db.session.query(func.max(Cart.order_id)).scalar() + 1
            if user.payment is None:
                flash("You payment is empty, please go to profile and add your payment")
                return redirect(url_for('customer_edit', id=user.id))
            cart_cake = Cart.query.filter_by(user_id=user.id, status="Not submitted").first()
            if cart_cake is None:
                flash("You have no cake to checkout")
                return redirect(url_for('menu'))
            cart_cake = Cart.query.filter_by(user_id=user.id, status="Not submitted")
            for i in cart_cake:
                i.status = "Submitted"
                i.order_id = index
                i.time_submit = datetime.utcnow()
            db.session.commit()
            flash("You have successful checkout your Cart item")
            return redirect(url_for('order_history'))
        return render_template('customers/checkout.html', user=user)
    else:
        if request.method == 'POST':
            first_name = request.values.get('first_name')
            last_name = request.values.get('last_name')
            email = request.values.get('email')
            address = request.values.get('address')
            card_name = request.values.get('cardname')
            card_number = request.values.get('cardnumber')
            expmonth = request.values.get('expmonth')
            expyear = request.values.get('expyear')
            cvv = request.values.get('cvv')
            billing = request.values.get('billing')
            if first_name == "" or last_name == "" or email == "" or address == "":
                flash("Personal field should not be empty.")
                return redirect(url_for('checkout'))
            if card_name == "" or card_number == "" or expmonth == "" or expyear == "" or cvv == "" or billing == "":
                flash("Payment field should not be empty")
                return redirect(url_for('checkout'))
            payment = card_name + "," + card_number + "," + expmonth + "," + expyear + "," + cvv
            exist_user = User.query.filter_by(email=email, first_name=first_name, last_name=last_name,
                                              address=address).first()
            if exist_user is None:
                add_user = User(email=email, address=address, role_id='1', first_name=first_name,
                                last_name=last_name, rating=0.0, store_id=1, number_of_warning=0,
                                order_made=0, blacklist=0, number_of_drop=0, payment=payment, billing_address=billing)
                db.session.add(add_user)
                db.session.commit()
            user = User.query.filter_by(email=email, first_name=first_name, last_name=last_name,
                                        address=address).first()
            cake_total = db.session.query(func.max(Cake.id)).scalar()
            index = db.session.query(func.max(Cart.order_id)).scalar() + 1
            count = 0
            for j in range(1, int(cake_total) + 1):
                if str(j) in session:
                    count += 1
                    i = str(j)
                    cake_id = session[i][0]
                    amount = session[i][1]
                    cook_id = session[i][2]
                    visitor_price = session[i][5]
                    temp = Cart(cake_id=cake_id, user_id=user.id, amount=amount,
                                price=visitor_price, status="Submitted", cook_id=cook_id, cake_rating=0,
                                deliver_rating=0, user_rating=0, store_rating=0, order_id=index,
                                time_submit=datetime.utcnow())
                    db.session.add(temp)
                    session.pop(i, None)
            if count == 0:
                flash("You have no items in Cart")
                return redirect(url_for('menu'))
            db.session.commit()
            flash("You have successful checkout your Cart items")
            return redirect(url_for('index'))
        return render_template('customers/checkout.html')


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
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        new_cardname = request.form.get('cardname')
        new_cardnumber = request.form.get('cardnumber')
        new_expired_month = request.form.get('expmonth')
        new_expired_year = request.form.get('expyear')
        new_cvv = request.form.get('cvv')
        new_billing_addr = request.form.get('billingaddr')
        try:
            if email != "":
                user.email = email
            if address != "":
                user.address = address
            if password != "" and confirm_password != "":
                if password == confirm_password:
                    user.set_password(password)
            if new_billing_addr != "":
                user.billing_address = new_billing_addr
            if new_cardname != "" or new_cardnumber != "" or new_expired_month != "" \
                    or new_expired_year != "" or new_cvv != "":
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
    counts = db.session.query(func.max(Cart.order_id)).scalar()
    carts = Cart.query.filter(or_(Cart.user_id == current_user.id, Cart.status == "Submitted",
                                  Cart.status == "In Process", Cart.status == "Closed"))
    return render_template('customers/order_history.html', carts=carts, counts=counts)


@app.route('/customer/rating/<id>', methods=['GET', 'POST'])
@login_required(1, 3, 4)
def rating(id):
    cart = Cart.query.filter_by(id=id).first()
    if request.method == "POST":
        if request.form.get('store_rating') is None:
            flash("Store rating is empty")
            return redirect(url_for('rating', id=id))
        store_rating = int(request.form.get('store_rating'))

        if request.form.get('deliver_rating') is None:
            flash("Deliver rating is empty")
            return redirect(url_for('rating', id=id))
        deliver_rating = int(request.form.get('deliver_rating'))

        if request.form.get('cake_rating') is None:
            flash("Cake rating is empty")
            return redirect(url_for('rating', id=id))
        cake_rating = int(request.form.get('cake_rating'))

        cake_comments = request.form.get('cake_comments')
        deliver_comments = request.form.get('deliver_comments')
        store_comments = request.form.get('store_comments')

        if store_rating < 3 and store_comments == '':
            flash("Rating lower than 3 must provide comments")
            return redirect(url_for('rating', id=id))
        if cake_rating < 3 and cake_comments == '':
            flash("Rating lower than 3 must provide comments")
            return redirect(url_for('rating', id=id))
        if deliver_rating < 3 and deliver_comments == '':
            flash("Rating lower than 3 must provide comments")
            return redirect(url_for('rating', id=id))

        cart.store_rating = store_rating
        cart.store_comments = store_comments
        cart.cake_rating = cake_rating
        cart.cake_comments = cake_comments
        cart.cake.order_made += 1
        if cart.cake.order_made == 1:
            cart.cake.rating = cake_rating
        elif cart.cake.order_made == 2:
            cart.cake.rating = (cake_rating + cart.cake.rating) / Decimal(2.0)
        else:  # cart.cake.order_made >= 3
            cart.cake.rating = (cake_rating + (2 * cart.cake.rating)) / Decimal(3.0)
            if cart.cake.rating < Decimal(2.0):
                temp = Cake.query.filter_by(id=cart.cake.id).first()
                db.session.delete(temp)
                flash("Cake " + str(cart.cake.cake_name) + " has been dropped.")
                cart.cook.number_of_drop += 1
                flash("Cook " + str(cart.cook_id) + " has been added a number of dropped")
                if cart.cook.number_of_drop >= 2:
                    cart.cook.number_of_warning += 1
                    flash("Cook has cake was dropped twice before, so there is a warning on his acc")
                    if cart.cook.number_of_warning > 3:
                        cart.cook.blacklist = True
                        flash("Cook has more than 3 warnings, therefore he/she is laid off")
                    cart.cook.number_of_drop = 0

        cart.deliver_rating = deliver_rating
        cart.deliver_comments = deliver_comments
        cart.deliver.order_made += 1
        if cart.deliver.order_made == 1:
            cart.deliver.rating = deliver_rating
        elif cart.deliver.order_made == 2:
            cart.deliver.rating = (deliver_rating + cart.deliver.rating) / Decimal(2.0)
        else:
            cart.deliver.rating = (deliver_rating + (2 * cart.deliver.rating)) / Decimal(3.0)
            if cart.deliver.rating < Decimal(2.0):
                cart.deliver.number_of_warning += 1
                flash("Deliver " + str(cart.deliver_id) + " has rating less than 2.0, therefore received a warning")
                if cart.deliver.number_of_warning > 3:
                    cart.deliver.blacklist = True
                    flash("Deliver has more than 3 warnings, therefore he/she is laid off")
        db.session.commit()
        flash("Thank you for your rating")
        return redirect(url_for("order_history"))
    return render_template('customers/rating.html', cart=cart)


########################################################################################################################
# Cook


@app.route('/cook')
@login_required(6)
def cook():
    cakes = Cake.query.all()
    return render_template('cooks/cook.html', title='Cook', cakes=cakes)


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
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            cakePic.save(path)
            newname = (request.values.get('cakeName')).replace(" ", "") + '.png'
            target = os.path.join(app.config['UPLOAD_FOLDER'], newname)
            os.rename(path, target)

            customerPirce = 0.95 * float(request.values.get('price'))
            vipPrice = 0.9 * float(request.values.get('price'))

            newCake = Cake(cake_name=request.values.get('cakeName'),
                           visitor_price=request.values.get('price'), customer_price=customerPirce, vip_price=vipPrice,
                           photo=newname, description=request.values.get('description'))

            db.session.add(newCake)
            db.session.commit()

            flash('success')
        else:
            flash('invalid file')
    return render_template('cooks/cookadditem.html', title='Cook')


@app.route('/cook/dropitem', methods=['GET', 'POST'])
def dropitem():
    cakes = Cake.query.all()

    if request.method == "POST":
        cake_name = request.values.get('cake')
        drop_cake = Cake.query.filter_by(cake_name=cake_name).first()
        if drop_cake is not None:
            db.session.delete(drop_cake)
            db.session.commit()
            flash("Successful delete item")

    return render_template('cooks/drop_item.html', title='Cook', cakes=cakes)


@app.route('/cook/edititem', methods=['GET', 'POST'])
def edititem():
    cakes = Cake.query.all()

    if request.method == "POST":
        cake_name = request.values.get('cake')
        edit_cake = Cake.query.filter_by(cake_name=cake_name).first()

        price = request.form.get('price')
        description = request.form.get('description')

        if price != "":
            edit_cake.visitor_price = price
            edit_cake.customer_price = 0.95 * float(price)
            edit_cake.vip_price = 0.9 * float(price)
        if description != "":
            edit_cake.description = description
        db.session.commit()
        flash('You have successfully edit item!')
    return render_template('cooks/edit_item.html', title='Cook', cakes=cakes)


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
        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
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

@app.route('/deliver')
@login_required(5)
def deliver():
    logs = Cart.query.filter_by(deliver_id=current_user.id, status="In process")
    return render_template('deliveries/delivery.html', title='Deliver', logs=logs)


@app.route('/deliver_rating/<id>', methods=['GET', 'POST'])
@login_required(5)
def deliver_rating(id):
    cart = Cart.query.filter_by(id=id).first()
    if request.method == 'POST':
        update_cart = Cart.query.filter_by(order_id=cart.order_id)
        user = User.query.filter_by(id=cart.user_id).first()
        rating = int(request.form.get('rate_list'))
        comments = request.form.get('comments')
        if rating < 3 and comments == "":
            flash("Comments must be provided if rating is less than 3")
            return redirect(url_for('deliver_rating', id=id))
        for i in update_cart:
            i.user_rating = rating
            i.user_comments = comments
            i.status = "Closed"
        user.order_made += 1
        user.rating = (user.rating + int(rating)) / Decimal(user.order_made)
        if user.order_made > 3 and user.rating > 4.0 and user.role_id == 3:
            user.role_id = 4  # VIP
        if user.order_made > 3 and 1 < user.rating < 2.0:
            user.role_id = 1  # demote to visitor
        if user.order_made > 3 and user.rating >= 1.0:
            user.blacklist = 1
            user.role_id = 1
        db.session.commit()
        flash("Thank you your rating and feedback")
        return redirect(url_for("deliver"))
    return render_template('deliveries/deliver_rating.html', cart=cart)


@app.route('/deliver/notification')
@login_required(5)
def notification():
    return render_template('deliveries/notification.html', title='Deliver')


@app.route('/deliver/profile/<id>')
@login_required(5)
def deliver_profile(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('deliveries/profile.html', user=user)


@app.route('/deliver/edit/<id>', methods=['GET', 'POST'])
@login_required(5)
def deliver_edit(id):
    user = User.query.filter_by(id=id).first_or_404()
    if request.method == "POST":
        email = request.form.get('new_email')

        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
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
    return render_template('deliveries/route.html', title='Deliver')


@app.route('/deliver/notification')
@login_required(5)
def deliver_notification():
    return render_template('deliveries/notification.html', title='Deliver')


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

        address = request.form.get('new_address')
        password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_new_password')
        try:
            if email != "":
                user.email = email
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


@app.route('/manager/CookWarning', methods=['GET', 'POST'])
@login_required(7)
def cookwarning():
    cook = User.query.filter_by(role_id=6)
    if request.method == "POST":
        target = int(request.form['erase'])
        cook_target = User.query.filter_by(id=target).first()
        if cook_target.number_of_warning > 0:
            cook_target.number_of_warning = cook_target.number_of_warning - 1
            db.session.commit()
            flash("Erase Successfully!")
    return render_template('managers/CookWarning.html', cook=cook)


@app.route('/manager/CustomerApplication', methods=['GET', 'POST'])
@login_required(7)
def application():
    me = User.query.filter(User.role_id == 1, User.blacklist == False,
                           User.password_hash != "")
    if request.method == 'POST':
        if request.values.get('approve'):
            user_id = int(request.values.get('approve'))
            user = User.query.filter_by(id=user_id).first()
            user.role_id = 3
            db.session.commit()
            flash("Success to approve " + user.first_name + " visitor to registered customer")
        else:
            user_id = int(request.values.get('decline'))
            user = User.query.filter_by(id=user_id).first()
            flash(user.blacklist)
            user.blacklist = True
            flash(user.blacklist)
            db.session.commit()
            flash("Success to decline " + user.first_name)
    return render_template('managers/CustomerApplication.html', me=me)


@app.route('/manager/CustomerComplaint')
@login_required(7)
def complaint():
    return render_template('managers/CustomerComplaint.html')


@app.route('/manager/order')
@login_required(7)
def order():
    carts = Cart.query.filter_by(status="Submitted")
    return render_template('managers/order.html', carts=carts)


@app.route('/manager/assign_order/<id>', methods=['GET', 'POST'])
@login_required(7)
def assign_order(id):
    cart = Cart.query.filter_by(id=id).first()
    delivers = User.query.filter_by(role_id=5)  # store_id = ?
    if request.method == 'POST':
        deliver_id = request.form['deliver']
        cart.status = "In process"
        cart.deliver_id = deliver_id
        db.session.commit()
        flash("Successful assigned deliver to this order: " + str(cart.id))
        return redirect(url_for("order"))
    return render_template('managers/assign_order.html', delivers=delivers, cart=cart)


@app.route('/manager/DeliverWarning', methods=['GET', 'POST'])
@login_required(7)
def deliverwarning():
    delivery = User.query.filter_by(role_id=5)
    if request.method == "POST":
        target = int(request.form['erase'])
        delivery_target = User.query.filter_by(id=target).first()
        if delivery_target.number_of_warning > 0:
            delivery_target.number_of_warning = delivery_target.number_of_warning - 1
            db.session.commit()
            flash("Erase Successfully!")
    return render_template('managers/DeliverWarning.html', delivery=delivery)


@app.route('/manager/ManageCustomers')
@login_required(7)
def managecustomers():
    return render_template('managers/ManageCustomers.html')


@app.route('/manager/PayWage', methods=['GET', 'POST'])
@login_required(7)
def paywage():
    delivery = User.query.filter_by(role_id=5)
    cook = User.query.filter_by(role_id=6)
    if request.method == 'POST':
        if request.form['action'] == "new_sheet":
            for i in delivery:
                if request.values.get('hours' + str(i.id)) == "":
                    i.salary = 0.0
                    db.session.commit()
            for j in cook:
                if request.values.get('hours' + str(j.id)) == "":
                    j.salary = 0.0
                    db.session.commit()
            flash("New salary sheet")

        if request.form['action'] == "submit_hours":
            for i in delivery:
                if request.values.get('hours' + str(i.id)) == "":
                    i.salary = i.salary
                else:
                    i.salary = float(request.values.get('hours' + str(i.id))) * 15
                    db.session.commit()
            for j in cook:
                if request.values.get('hours' + str(j.id)) == "":
                    j.salary = j.salary
                else:
                    j.salary = float(request.values.get('hours' + str(j.id))) * 20
                    db.session.commit()
            flash("Submit Successfully!")
    return render_template('managers/PayWage.html', delivery=delivery, cook=cook, delivery_salary_rate=15,
                           cook_salary_rate=20)


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
    if 'user_address' not in session:
        flash("User Address not provide")
        return redirect(url_for('mapforcust'))
    if 'store_address' not in session:
        flash("Store Address not provide")
        return redirect(url_for('mapforcust'))
    session['store_address'] = [x, y]
    session['user_address'] = [c_x, c_y]
    print(x)
    print(y)
    print(c_x)
    print(c_y)
    # x,y --> store -> products model
    return jsonify('success')


@app.route('/mapfordelivery')
@login_required(5)
def mapfordeli():
    return render_template('/MapForDelivery.html')
