from flask import Flask, jsonify, request, current_app
import requests
from .utils import check_authentication
from .models import db, Clown

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['CLIENTS_SERVICE_URL'] = 'http://localhost:5000'
current_app.config['Troup_Leader_SERVICE_URL'] = 'http://localhost:5000'
db.init_app(app)

# Endpoint to get a list of appointments for a specific clown
@app.route('/appointments', methods=['GET'])
def get_appointments():
    clown_id = request.headers.get('X-Clown-ID')
    if check_authentication(clown_id):

        # User helper method to request clown appointments from troup leader service
        appointments = get_clown_appointments(clown_id)
        return jsonify(appointments)
    else:
        return jsonify({'message': 'Unauthorized'}), 401


# Endpoint to report an issue with an appointment
@app.route('/appointments/<int:appointment_id>/issues', methods=['POST'])
def report_issue(appointment_id):
    clown_id = request.headers.get('X-Clown-ID')
    if check_authentication(clown_id):

        # User helper method to request appointment from troup leader service
        appointment = get_appointment(appointment_id)
        if appointment['clown_id'] == clown_id:
            issue = request.json.get('issue')

            # Send issue to troup leader service
            issue_url = f'http://localhost:5000/appointments/{id}/issues'
            data = {'issue': issue}
            response = requests.put(issue_url, json=data)
            db.session.commit()

            if response.status_code != 200:
                return jsonify({'error': 'Failed to report issue'}), 500

            return jsonify({'message': 'issue reported successfully'}), 200

        else:
            return jsonify({'message': 'Unauthorized'}), 401
    else:
        return jsonify({'message': 'Unauthorized'}), 401


# Endpoint to request client contact details for an appointment
@app.route('/appointments/<int:appointment_id>/client', methods=['GET'])
def request_client_details(appointment_id):
    clown_id = request.headers.get('X-Clown-ID')
    if check_authentication(clown_id):

        # User helper method to request appointment from troup leader service
        appointment = get_appointment(appointment_id)

        # If appointment belongs to clown get client id and request client details from client service using helper
        # method
        if appointment.clown_id == clown_id:
            client_id = appointment.client_id
            client_details = get_client_details(client_id)
            return jsonify({
                'client_name': client_details['name'],
                'client_phone': client_details['phone']
            })
        else:
            return jsonify({'message': 'Unauthorized'}), 401
    else:
        return jsonify({'message': 'Unauthorized'}), 401

# Endpoint that allows troup leader to get a specific clown or update clowns appointment
@app.route('/clowns/<int:clown_id>', methods=['GET', 'PUT'])
def handle_clown(clown_id):
    clown = Clown.query.get(clown_id)
    if not clown:
        return jsonify({'error': 'Clown not found'}), 404

    if request.method == 'GET':
        return jsonify(clown.to_dict())

    elif request.method == 'PUT':
        data = request.get_json()
        clown.name = data.get('name', clown.name)
        clown.appointments = data.get('appointments', clown.appointments)
        db.session.commit()
        return jsonify(clown.to_dict())

# Endpoint that allows clowns to manage their appointments
@app.route('/clowns/<int:clown_id>/appointments', methods=['POST', 'DELETE'])
def handle_appointments(clown_id):
    clown = Clown.query.get(clown_id)
    if not clown:
        return jsonify({'error': 'Clown not found'}), 404

    # if method is post, add apointment to clown
    if request.method == 'POST':
        data = request.get_json()
        appointment_id = data.get('appointment_id')
        if appointment_id not in clown.appointments:
            clown.add_appointment(appointment_id)
            db.session.commit()
            return jsonify({'message': 'Appointment added to clown.'})
        else:
            return jsonify({'error': 'Appointment already exists.'}), 400

    # if method is delete, remove appointment from clown
    elif request.method == 'DELETE':
        data = request.get_json()
        appointment_id = data.get('appointment_id')
        if appointment_id in clown.appointments:
            clown.remove_appointment(appointment_id)
            db.session.commit()
            return jsonify({'message': 'Appointment removed from clown.'})
        else:
            return jsonify({'error': 'Appointment not found.'}), 404


# Helper function to get a list of appointments for a specific clown
# Makes request to troup leader service
def get_clown_appointments(clown_id):
    appointments_service_url = current_app.config['Troup_Leader_SERVICE_URL']
    appointments_response = requests.get(f'{appointments_service_url}/clown/{clown_id}')
    if appointments_response.status_code == 200:
        return appointments_response.json().get('appointments', [])
    return []


# Helper function to get the details of an appointment
# Makes request to troup leader service
def get_appointment(appointment_id):
    appointments_service_url = current_app.config['Troup_Leader_SERVICE_URL']
    appointment_response = requests.get(f'{appointments_service_url}/appointments/{appointment_id}')
    if appointment_response.status_code == 200:
        appointment_data = appointment_response.json().get('appointment', {})
        return appointment_data
    return None


# Helper function to get the details of a client
# Makes request to client service
def get_client_details(client_id):
    clients_service_url = current_app.config['CLIENTS_SERVICE_URL']
    client_response = requests.get(f'{clients_service_url}/clients/{client_id}')
    if client_response.status_code == 200:
        return client_response.json()
    return {}
