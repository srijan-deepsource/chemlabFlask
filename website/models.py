from flask_login import UserMixin
from datetime import datetime
from . import db


class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(150), unique=True)
    total_stock = db.Column(db.Integer)
    available_stock = db.Column(db.Integer)
    price = db.Column(db.Integer)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    password = db.Column(db.String(150))
    when_joined = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    balance = db.Column(db.Integer, default=100)
    rentals = db.relation('Orders')


class Orders(db.Model):
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    quantity = db.Column(db.Integer)
    when_rented = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    returned = db.Column(db.Boolean, default=False)
    when_returned = db.Column(db.DateTime(timezone=True), default=datetime.utcnow())
    amount = db.Column(db.Integer, default=0)
    hours = db.Column(db.Integer, default=0)
    item = db.relation('Items')
    user = db.relation('User')
