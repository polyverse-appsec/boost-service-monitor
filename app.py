from chalice import Chalice

from chalicelib.app_utils import test_api_status

app = Chalice(app_name='boost-monitor')

aws_server = ".lambda-url.us-west-2.on.aws/"

prod_analyze = "https://2av3vd7bxvxu3zfymtdgqziuoy0lvpge" + aws_server
prod_analyze_function = "https://scqfjxbrko57bekv4lqkvu24fa0cmapi" + aws_server
prod_codeguidelines = "https://ssmhqxozg6ixnk5abyhnezf5ya0seyby" + aws_server
prod_user_organizations = "https://ptb5spl6kvsuioc5zkrgyncrve0jyrew" + aws_server
prod_compliance = "https://7vtdrtujboyw4ft7af7j2aimqi0wzwzd" + aws_server
prod_blueprint = "https://hb34ftyxhjnd7jvxbmlsmddct40hvrni" + aws_server
prod_flowdiagram = "https://b3pflzry5l5wbaenwtdytiv7se0ykzkc" + aws_server
prod_customer_portal = "https://roxbi254sch3yijt7tqbz4s7jq0jxddr" + aws_server
prod_compliance_function = "https://srsybz6dbjz45skdwq6quou4ua0rxbnk" + aws_server
prod_customprocess = "https://7ntcvdqj4r23uklomzmeiwq7nq0dhblq" + aws_server
prod_generate = "https://egw2c7dn5vz3leffr3mfqodx3a0perwp" + aws_server
prod_testgen = "https://mqxkx5m7hehbskfvrcfwctbt7y0gghab" + aws_server
prod_explain = "https://vdcg2nzj2jtzmtzzcmfwbvg4ey0jxghj" + aws_server
prod_summarize = "https://tu5zdmjxvvzbzih6yytjtbm6fa0uvjba" + aws_server


@app.lambda_function(name='monitor_user_organizations')
def monitor_user_organizations(event, _):
    results_test = {'organizations'}

    return test_api_status("user_organizations", prod_user_organizations, None, results_test)


@app.lambda_function(name='monitor_customer_portal')
def monitor_customer_portal(event, _):
    results_test = {'status', 'portal_url'}

    return test_api_status("customer_portal", prod_customer_portal, None, results_test)


@app.lambda_function(name='monitor_explain')
def monitor_explain(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'explanation', 'chunked', 'truncated'}

    response = test_api_status("explain", prod_explain,
                               request_body, results_test)

    return response
