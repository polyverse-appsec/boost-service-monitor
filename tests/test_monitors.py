from chalice.test import Client
from app import app


def _test_monitor(monitor):
    with Client(app) as client:

        response = client.lambda_.invoke(
            f'monitor_{monitor}')

        assert response.payload['statusCode'] == 200


def test_monitor_user_organizations():
    _test_monitor('user_organizations')


def test_monitor_customer_portal():
    _test_monitor('customer_portal')


def test_monitor_explain():
    _test_monitor('explain')


def test_monitor_flowdiagram():
    _test_monitor('flowdiagram')


def test_monitor_analyze():
    _test_monitor('analyze')


def test_monitor_analyze_function():
    _test_monitor('analyze_function')


def test_monitor_compliance():
    _test_monitor('compliance')


def test_monitor_compliance_function():
    _test_monitor('compliance_function')


def test_monitor_codeguidelines():
    _test_monitor('codeguidelines')


def test_monitor_summarize():
    _test_monitor('summarize')


def test_monitor_generate():
    _test_monitor('generate')


def test_monitor_testgen():
    _test_monitor('testgen')


def test_monitor_blueprint():
    _test_monitor('blueprint')


def test_monitor_customprocess():
    _test_monitor('customprocess')


def test_monitor_performance():
    _test_monitor('performance')


def test_monitor_performance_function():
    _test_monitor('performance_function')


def test_monitor_quick_blueprint():
    _test_monitor('quick-blueprint')


def test_monitor_draft_blueprint():
    _test_monitor('draft-blueprint')
