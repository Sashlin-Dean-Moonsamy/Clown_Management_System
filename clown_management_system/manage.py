# Manage.py file to adopt django scaffold

# Imports apps from services
from authentication_service.views import app as auth_service_app
from client_service.views import app as client_service_app
from troup_leader_service.views import app as troup_leader_service_app
from clown_service.views import app as clown_service_app

# Run apps
if __name__ == '__main__':
    auth_service_app.run()
    client_service_app.run()
    troup_leader_service_app.run()
    clown_service_app.run()
