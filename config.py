import os

class Config:
    SECRET_KEY = os.environ.get('secret_key') or 'secret_key_de_desarrollo'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tickets.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
