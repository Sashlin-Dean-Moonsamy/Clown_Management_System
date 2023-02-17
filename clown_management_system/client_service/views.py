from flask import request, jsonify, g, Flask
import requests

from .utils import check_authentication
from .models import Client, ClientSchema, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)
db.init_app(app)

@app.route("/clients", methods=["GET"])
def get_clients():
    clients = Client.query.all()
    result = clients_schema.dump(clients)
    return jsonify(result.data)


@app.route("/clients", methods=["POST"])
def add_client():
    # Check if user is authenticated
    client = Client(g.user.id, **request.json)
    if not check_authentication(client.id):
        return jsonify({'error': 'Unauthorized'}), 401

    db.session.add(client)
    db.session.commit()
    return client_schema.jsonify(client)


@app.route("/clients/<int:id>", methods=["GET"])
def get_client(id):
    client = Client.query.get(id)
    return client_schema.jsonify(client)


@app.route("/clients/<int:id>", methods=["PUT"])
def update_client(id):
    # Check if user is authenticated
    client = Client.query.get(id)
    if not check_authentication(client.id):
        return jsonify({'error': 'Unauthorized'}), 401

    client.contact_name = request.json['contact_name']
    client.contact_email = request.json['contact_email']
    client.contact_number = request.json['contact_number']
    db.session.commit()
    return client_schema.jsonify(client)

# Endpoint to get a clients appointment
@app.route("/clients/<int:id>/appointments", methods=["GET"])
def get_client_appointments(id):

    # get client object and authenticate
    client = Client.query.get(id)
    if not check_authentication(client.id):
        return jsonify({'error': 'Unauthorized'}), 401

    # Retrieve appointments from troup leader service and return data or error
    appointments_url = 'http://localhost:5000/appointments'
    params = {'client_id': id}
    response = requests.get(appointments_url, params=params)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve appointments'}), 500

    appointments = response.json()
    return jsonify(appointments)

# Endpoint for client to rate an appointment
@app.route('/appointments/<int:id>/rate', methods=['POST'])
def rate_appointment(id):

    # Authenticate client
    if not check_authentication(id):
        return jsonify({'error': 'Unauthorized'}), 401

    # request appointment from troup leader service
    appointment_url = f'http://localhost:5000/appointments/{id}'
    response = requests.get(appointment_url)

    if response.status_code != 200:
        return jsonify({'error': 'Appointment not found'}), 404

    appointment = response.json()

    # Check if appointment belongs to client
    if appointment['client_id'] != id:
        return jsonify({'error': 'Appointment does not belong to client'}), 403

    # Get rating from request body
    rating = request.json.get('rating')

    # Send rating to troup leader service
    rating_url = f'http://localhost:5000/appointments/{id}/rate'
    data = {'rating': rating}
    response = requests.put(rating_url, json=data)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to rate appointment'}), 500

    return jsonify({'message': 'Appointment rated successfully'}), 200
