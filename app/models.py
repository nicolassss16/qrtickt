from . import db
from flask_login import UserMixin
import uuid

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

class Event(db.Model):
    __tablename__ = 'event'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # Relación con tickets (cascade para eliminar tickets si se borra evento)
    tickets = db.relationship('Ticket', backref='event', lazy=True, cascade='all, delete-orphan')

class Ticket(db.Model):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nombre del comprador
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    qr_code = db.Column(db.Text, nullable=False)  # Base64 de la imagen QR
    ticket_code = db.Column(db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    usado = db.Column(db.Boolean, default=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(36))

    # No hace falta declarar la relación inversa aquí porque está en Event.tickets
