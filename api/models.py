from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    scan_data = db.Column(db.Text(), nullable=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now(), nullable=False)
    task_id = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    reports = db.relationship('Report')
    role = db.Column(db.Integer, default=0)