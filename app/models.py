from flask_login import UserMixin
from .extensions import db


class Donate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Firstname = db.Column(db.String(100), nullable=False)
    Lastname = db.Column(db.String(100), nullable=False)
    Address = db.Column(db.String(100), nullable=False)
    Email = db.Column(db.String(100), nullable=False)
    Image = db.Column(db.String(100), nullable=False)
    Amount = db.Column(db.Integer, nullable=False)


class Animal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    catagory = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(200), nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<user> {self.username}"


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    eventname = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(200), nullable=False)