from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", back_populates="client")
    contact_name = db.Column(db.String(128))
    contact_email = db.Column(db.String(128))
    contact_number = db.Column(db.String(16))


class ClientSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Client
