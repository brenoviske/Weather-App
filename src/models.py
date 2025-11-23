from base import db


class User(db.Model):

    __tablename__ = 'users'

    email = db.Column(db.String(200), primary_key=True, nullable=False)
    username = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(512), nullable=False)