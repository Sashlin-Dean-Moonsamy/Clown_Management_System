import requests
from flask import current_app


def check_authentication(user_id):
    auth_service_url = current_app.config['AUTH_SERVICE_URL']
    auth_response = requests.get(f'{auth_service_url}/is_authenticated/{user_id}')
    if auth_response.status_code == 200:
        return auth_response.json().get('is_authenticated', False)
    return False
