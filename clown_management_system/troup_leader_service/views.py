from flask import Flask, request, jsonify, g
import requests
from .models import Appointment, db
from .utils import check_authentication

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@hostname/database'
db.init_app(app)


# Endpoint to create appointment
@app.route('/appointments', methods=['POST'])
def create_appointment():

    # Authenticate troup leader
    troupe_leader_id = request.headers.get('Troupe-Leader-ID')
    if not check_authentication(troupe_leader_id):
        return jsonify({'error': 'Unauthorized'}), 401

    # Get appointment information and create appointment
    clown_id = request.json.get('clown_id')
    client_id = request.json.get('client_id')
    appointment_date = request.json.get('appointment_date')
    appointment = Appointment(troupe_leader_id=troupe_leader_id, client_id=client_id, clown_id=clown_id,
                              date=appointment_date)
    db.session.add(appointment)
    db.session.commit()

    # Make a request to the clown microservice to get the clown with the specified ID
    clown_service_url = 'http://localhost:5000'
    response = requests.get(f'{clown_service_url}/clowns/{clown_id}')

    # If the clown is found, add the appointment to their list of appointments
    if response.status_code == 200:
        clown_data = response.json()
        appointments = clown_data.get('appointments', [])
        if appointment.id not in appointments:
            appointments.append(appointment.id)

            # Send updated appointments to clown service to update clown
            response = requests.put(f'{clown_service_url}/clowns/{clown_id}', json={'appointments': appointments})
            if response.status_code == 200:
                return jsonify({'message': 'Appointment added to clown.'})
            else:
                return jsonify({'error': 'Failed to update clown data.'}), 500
        else:
            return jsonify({'error': 'Appointment already exists.'}), 400
    else:
        return jsonify({'error': 'Clown not found.'}), 404


# An endpoint to retrieve appointments for a specific client
@app.route('/appointments', methods=['GET'])
def get_appointments():

    # Get and loop over appointments
    appointments = Appointment.query.all()
    result = []
    for appointment in appointments:

        # Validate if appointment beings to client and add it to results list
        if appointment.client_id == request.json.get('client_id'):
            result.append({
                'id': appointment.id,
                'troupe_leader_id': appointment.troupe_leader_id,
                'clown_id': appointment.clown_id,
                'client_id': appointment.client_id,
                'date': appointment.date.isoformat()
            })
    return jsonify(result)


# Endpoint for clowns service to receive all their appointments
@app.route('/appointments/clown/<int:id>', methods=['GET'])
def get_clown_appointments(id):
    appointments = Appointment.query.all()
    result = []
    for appointment in appointments:
        if appointment.clown_id == id:
            result.append({
                'id': appointment.id,
                'troupe_leader_id': appointment.troupe_leader_id,
                'clown_id': appointment.clown_id,
                'client_id': appointment.client_id,
                'date': appointment.date.isoformat()
            })
    return jsonify(result)

# Endpoint to get a specific appointment using appointment id
@app.route('/appointments/<int:id>', methods=['GET'])
def get_appointment(id):
    appointments = Appointment.query.get(id)

    if appointments is None:
        return {}
    return jsonify(appointments)


# Endpoint for client service to rate an appointment
@app.route('/appointments/<int:id>/rate', methods=['PUT'])
def update_appointment_rating(id):
    appointment = Appointment.query.get(id)

    # Validate appointment
    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if not check_authentication(appointment.troup_leader_id):
        return jsonify({'error': 'Unauthorized'}), 401

    # get new rating from client service and validate
    new_rating = request.json.get('rating')

    if not new_rating:
        return jsonify({'error': 'Invalid rating'}), 400

    # make change
    appointment.rating = new_rating
    db.session.commit()

    return jsonify({'message': 'Appointment rating updated successfully'}), 200


# Endpoint for clowns to update an appointment issue
@app.route('/appointments/<int:id>/issues', methods=['PUT'])
def update_appointment_issue(id):

    # Get all appointment with appointment id and validate
    appointment = Appointment.query.get(id)

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    if not check_authentication(appointment.troup_leader_id):
        return jsonify({'error': 'Unauthorized'}), 401

    # Get new issue form clown service and validate
    new_issue = request.json.get('issue')

    if not new_issue:
        return jsonify({'error': 'Invalid issue'}), 400

    # Make change
    appointment.issue = new_issue
    db.session.commit()

    return jsonify({'message': 'Appointment issue updated successfully'}), 200
