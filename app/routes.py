from app import app  # db
from flask import render_template, flash, redirect, request, url_for
# from app.forms import EditProfileForm, LoginForm, RegistrationForm
# from app.models import User
# from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime
from functools import wraps


# from flask_login import LoginManager


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/menu')
def menu():
    return render_template('menu.html', title='Menu')

########################################################################################################################
#Customer


@app.route('/customer/description')
def description():
    return render_template('customers/description.html')


@app.route('/customer/registration')
def registration():
    return render_template('customers/registerform.html')


@app.route('/checkout')
def checkout():
    return render_template('customers/checkout.html', title='Menu')


@app.route('/confirmation')
def confirmation():
    return render_template('customers/confirmation.html', title='Menu')


@app.route('/customer/customer_profile')
def customer_profile():
    return render_template('customers/customer_profile.html', title='Menu')


@app.route('/customer/order_history')
def order_history():
    return render_template('customers/order_history.html', title='Menu')


@app.route('/customer/rating')
def rating():
    return render_template('customers/rating.html', title='Menu')

########################################################################################################################
#Cook


@app.route('/cook')
def cook():
    return render_template('cooks/cook.html', title='Cook')


@app.route('/cook/additem')
def additem():
    return render_template('cooks/cookadditem.html', title='Cook')


@app.route('/cook/cook_profile')
def cook_profile():
    return render_template('cooks/cook_profile.html', title='Cook')


@app.route('/cook/dropped_notification')
def dropped_notification():
    return render_template('cooks/dropped_noti.html', title='Cook')


@app.route('/cook/warning_notification')
def warning_notification():
    return render_template('cooks/warning_noti.html', title='Cook')


########################################################################################################################
#Delivery

@app.route('/delivery')
def delivery():
    return render_template('deliveries/delivery.html', title='Delivery')


@app.route('/delivery/notification')
def notification():
    return render_template('deliveries/notification.html', title='Delivery')


@app.route('/delivery/profile')
def delivery_profile():
    return render_template('deliveries/profile.html', title='Delivery')


@app.route('/delivery/route')
def delivery_route():
    return render_template('deliveries/route.html', title='Delivery')

########################################################################################################################
#Manager


@app.route('/manager')
def manager():
    return render_template('managers/manager.html', title='Manager')


@app.route('/manager/CookWarning')
def CookWarning():
    return render_template('managers/CookWarning.html')


@app.route('/manager/CustomerApplication')
def application():
    return render_template('managers/CustomerApplication.html')


@app.route('/manager/CustomerComplaint')
def complaint():
    return render_template('managers/CustomerComplaint.html')


@app.route('/manager/DecideDelivery')
def decidedelivery():
    return render_template('managers/DecideDelivery.html')


@app.route('/manager/DeliverWarning')
def deliverwarning():
    return render_template('managers/DeliverWarning.html')


@app.route('/manager/ManageCustomers')
def managecustomers():
    return render_template('managers/ManageCustomers.html')


@app.route('/manager/PayWage')
def paywage():
    return render_template('managers/PayWage.html')










