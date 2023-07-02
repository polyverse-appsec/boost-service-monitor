from chalice import Chalice

from chalicelib.app_utils import test_api_status

app = Chalice(app_name='boost-monitor')

aws_server = ".lambda-url.us-west-2.on.aws/"

user_orgs = "https://cro3oyez4g56b33hvglfwytg3q0alxrz" + aws_server
customer_portal = "https://hry4lqp3ktulatehaowyzhkbja0mkjob" + aws_server


@app.lambda_function(name='monitor_user_organizations')
def monitor_user_organizations(event, _):
    return test_api_status("user_organizations", user_orgs)


@app.lambda_function(name='monitor_customer_portal')
def monitor_customer_portal(event, _):
    return test_api_status("customer_portal", customer_portal)
