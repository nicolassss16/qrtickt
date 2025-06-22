from . import db

class Event(db.Model): # database configuration
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    qr_code = db.Column(db.Text, nullable=False)
    usado = db.Column(db.Boolean, default=False)

