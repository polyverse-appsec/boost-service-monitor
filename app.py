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

    return test_api_status("explain", prod_explain,
                           request_body, results_test)


@app.lambda_function(name='monitor_testgen')
def monitor_testgen(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'testcode', 'chunked', 'truncated'}

    return test_api_status("", prod_testgen,
                           request_body, results_test)


key_ChunkPrefix = 'chunk_prefix'
key_NumberOfChunks = 'chunks'
key_IsChunked = 'chunked'


@app.lambda_function(name='monitor_summarize')
def monitor_summarize(event, _):
    request_body = {
        'inputs': 'first sentence\nsecond sentence\nthird sentence',
        'analysis_label': 'Explanation',
        'analysis_type': 'explain',
    }
    results_test = {'analysis_label', 'analysis_type', 'analysis', key_IsChunked, 'truncated'}

    response = test_api_status("summarize", prod_summarize, request_body, results_test)

    request_body = {
        'chunk_0': 'first sentence',
        'chunk_1': 'second sentence',
        'chunk_2': 'third sentence',
        'chunks': 3,
        'chunk_prefix': 'chunk_',
        'analysis_label': 'Explanation',
        'analysis_type': 'explain',
    }
    results_test = {'analysis_label', 'analysis_type', 'analysis', key_IsChunked, 'truncated'}

    response2 = test_api_status("summarize", prod_summarize,
                                request_body, results_test)

    return response if not response['statusCode'] == 200 or not response['isSuccessful'] or not response['functionalPass'] else response2


@app.lambda_function(name='monitor_flowdiagram')
def monitor_flowdiagram(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("flowdiagram", prod_flowdiagram,
                           request_body, results_test)


@app.lambda_function(name='monitor_analyze')
def monitor_analyze(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("analyze", prod_analyze,
                           request_body, results_test)


@app.lambda_function(name='monitor_analyze_function')
def monitor_(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
        'inputMetadata': {'lineNumberBase': 0}
    }
    results_test = {'status', 'details', 'chunked', 'truncated'}

    return test_api_status("", prod_analyze_function,
                           request_body, results_test)


@app.lambda_function(name='monitor_compliance')
def monitor_compliance(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("compliance", prod_compliance,
                           request_body, results_test)


@app.lambda_function(name='monitor_compliance_function')
def monitor_compliance_function(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
        'inputMetadata': {'lineNumberBase': 0}
    }
    results_test = {'status', 'details', 'chunked', 'truncated'}

    return test_api_status("compliance_function", prod_compliance_function,
                           request_body, results_test)


@app.lambda_function(name='monitor_blueprint')
def monitor_blueprint(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'blueprint', 'chunked', 'truncated'}

    return test_api_status("blueprint", prod_blueprint,
                           request_body, results_test)


@app.lambda_function(name='monitor_codeguidelines')
def monitor_codeguidelines(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("codeguidelines", prod_codeguidelines,
                           request_body, results_test)


@app.lambda_function(name='monitor_generate')
def monitor_generate(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
        'explanation': 'This code is a simple hello world program.',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("generate", prod_generate,
                           request_body, results_test)


@app.lambda_function(name='monitor_customprocess')
def monitor_customprocess(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}

    return test_api_status("customprocess", prod_customprocess,
                           request_body, results_test)