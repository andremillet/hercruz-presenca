from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)  # CPF format: XXX.XXX.XXX-XX
    crm = db.Column(db.String(20), nullable=True)  # CRM for doctors/nurses
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'plantonista', 'rotina'
    password = db.Column(db.String(200), nullable=False)  # For basic auth, will be hashed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='user', lazy=True)

class Shift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'day_shift', 'night_shift', 'routine'
    nurse_group = db.Column(db.String(10))  # '3-4', '5-6'
    assigned_users = db.Column(db.Text)  # JSON string of user_ids
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendances = db.relationship('Attendance', backref='shift', lazy=True)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'), nullable=False)
    check_in = db.Column(db.DateTime)
    check_out = db.Column(db.DateTime)
    hours_worked = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)