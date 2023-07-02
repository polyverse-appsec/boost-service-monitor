from chalice.test import Client
from app import app

client_version = '0.9.5'
request_body = {
    'session': 'testemail: boostmonitor@polytest.ai',
    'organization': 'polytest.ai',
    'version': client_version
}


def test_monitor_user_organizations():
    with Client(app) as client:

        response = client.lambda_.invoke(
            'monitor_user_organizations', request_body)

        assert response.payload['statusCode'] == 200


def test_monitor_ccustomer_portal():
    with Client(app) as client:
        response = client.lambda_.invoke(
            'monitor_customer_portal', request_body)

        assert response.payload['statusCode'] == 200
