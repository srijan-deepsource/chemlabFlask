from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from .models import Orders, Items
from . import db
import json
from math import ceil
from werkzeug.security import generate_password_hash, check_password_hash
import yaml
from sqlalchemy.exc import IntegrityError

views = Blueprint('views', __name__)


@views.route('/rent', methods=['GET', 'POST'])
@login_required
def rent():
    if request.method == 'POST':
        item_name = request.form.get('item')
        quantity = int(request.form.get('quantity'))
        item = Items.query.filter_by(item_name=item_name).first()
        available_stock = item.available_stock
        if available_stock < quantity:
            flash(f"Could not place order, only {available_stock} {item_name}(s) currently in stock", category='danger')
        elif current_user.balance < 0:
            flash(f"Could not rent item, balance too low.", category="danger")
        else:
            item.available_stock -= quantity
            order = Orders(item_id=item.item_id, user_id=current_user.id, quantity=quantity,
                           when_rented=datetime.utcnow())
            db.session.add(order)
            db.session.commit()
            flash("Item Rented Successfully!", category='success')
            return redirect(url_for('views.home'))
    items = Items.query.all()
    return render_template("rent.html", user=current_user, items_list=items)


@views.route('/')
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route('/return-item', methods=['POST'])
def return_item():
    if request.method == 'POST':
        data = json.loads(request.data)
        order_id = data['order_id']
        order = Orders.query.filter_by(order_id=order_id).first()
        order.item.available_stock += order.quantity
        order.when_returned = datetime.utcnow()
        order.returned = True
        db.session.commit()
        time_difference = order.when_returned - order.when_rented
        seconds = time_difference.total_seconds()
        hours = seconds / 3600
        hours = ceil(hours)
        amount = order.quantity * order.item.price * hours
        order.user.balance -= amount
        order.amount = amount
        order.hours = hours
        db.session.commit()
        flash('Item returned', category='success')
    return jsonify({})


@views.route('/add-balance', methods=['POST', 'GET'])
@login_required
def add_balance():
    if request.method == 'POST':
        balance = int(request.form.get('balance'))
        current_user.balance += balance
        db.session.commit()
        flash('Balance added successfully.', category='success')
        return redirect(url_for('views.home'))
    return render_template("add_balance.html", user=current_user)


@views.route('/change-password', methods=['POST', 'GET'])
@login_required
def change_password():
    if request.method == 'POST':
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        current_password = request.form.get('current_password')
        if not check_password_hash(current_user.password, current_password):
            flash('Current password is incorrect.', category='danger')
        elif password1 != password2:
            flash('Passwords do not match.', category='danger')
        else:
            current_user.password = generate_password_hash(password1, method="sha256")
            db.session.commit()
            flash("Password changed successfully!", category='success')
            return redirect(url_for('views.home'))
    return render_template("change_password.html", user=current_user)


@views.before_app_first_request
def add_default_items():
    with open('website/items.yaml') as fh:
        data = yaml.load(fh, Loader=yaml.FullLoader)
    for item in data.keys():
        item_name = data[item]['item_name']
        total_stock = data[item]['total_stock']
        available_stock = data[item]['available_stock']
        price = data[item]['price']
        item = Items(item_name=item_name, total_stock=total_stock, available_stock=available_stock, price=price)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
