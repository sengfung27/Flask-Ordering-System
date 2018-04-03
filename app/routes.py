
from app import app  # db
from flask import render_template, flash, redirect, request, url_for
#from app.forms import EditProfileForm, LoginForm, RegistrationForm
#from app.models import User
#from flask_login import current_user, login_user, logout_user
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

@app.route('/manager')

def manager():
    return render_template('managers/manager.html', title='Manager')


@app.route('/cook')

def cook():
    return render_template('cooks/cook.html', title='Cook')


@app.route('/delivery')

def delivery():
    return render_template('deliveries/delivery.html', title='Delivery')


@app.route('/map')

def map():
    return render_template('deliveries/map.html')


@app.route('/prices')

def prices():
    return render_template('cooks/prices.html')


@app.route('/cookcustorder')

def cookcustorder():
    return render_template('cooks/cookcustorder.html')


@app.route('/complaints')

def complaints():
    return render_template('managers/complaints.html')


@app.route('/payroll')
def payroll():
    return render_template('managers/payroll.html')


