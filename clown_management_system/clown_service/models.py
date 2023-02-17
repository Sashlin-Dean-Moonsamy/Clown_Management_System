from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()

# Create clown class with appointments as a list value and methods to edit it.
class Clown:
    def __init__(self, id, name, appointments=None):
        self.id = id
        self.name = name
        self.appointments = appointments or []

    def add_appointment(self, appointment_id):
        if appointment_id not in self.appointments:
            self.appointments.append(appointment_id)

    def remove_appointment(self, appointment_id):
        if appointment_id in self.appointments:
            self.appointments.remove(appointment_id)

