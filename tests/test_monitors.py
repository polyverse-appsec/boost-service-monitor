from chalice.test import Client
from app import app


def test_monitor_user_organizations():
    with Client(app) as client:

        response = client.lambda_.invoke(
            'monitor_user_organizations')

        assert response.payload['statusCode'] == 200


def test_monitor_ccustomer_portal():
    with Client(app) as client:
        response = client.lambda_.invoke(
            'monitor_customer_portal')

        assert response.payload['statusCode'] == 200


def test_monitor_explain():
    with Client(app) as client:
        response = client.lambda_.invoke(
            'monitor_explain')

        assert response.payload['statusCode'] == 200
