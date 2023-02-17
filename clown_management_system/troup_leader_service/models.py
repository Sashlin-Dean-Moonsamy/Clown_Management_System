from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()


# Define the TroupLeader model
class TroupLeader(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __init__(self, email, password):
        self.email = email
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)


class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    troup_leader_id = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    clown_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    issue = db.Column(db.String(120), nullable=True)

    def __init__(self, troup_leader_id, client_id, clown_id, date, rating=None):
        self.troup_leader_id = troup_leader_id
        self.client_id = client_id
        self.clown_id = clown_id
        self.date = date
        self.rating = rating
