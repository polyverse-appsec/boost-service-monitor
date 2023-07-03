from chalice import Chalice
import os
import json

from chalicelib.app_utils import test_api_status

app = Chalice(app_name='boost-monitor')

aws_server = ".lambda-url.us-west-2.on.aws/"

# Determine the stage by checking the CHALICE_STAGE environment variable
stage = os.getenv('CHALICE_STAGE', 'dev')

service_uris = {
    'prod': {
        'analyze': "https://2av3vd7bxvxu3zfymtdgqziuoy0lvpge" + aws_server,
        'codeguidelines': "https://ssmhqxozg6ixnk5abyhnezf5ya0seyby" + aws_server,
        'user_organizations': "https://ptb5spl6kvsuioc5zkrgyncrve0jyrew" + aws_server,
        'compliance': "https://7vtdrtujboyw4ft7af7j2aimqi0wzwzd" + aws_server,
        'blueprint': "https://hb34ftyxhjnd7jvxbmlsmddct40hvrni" + aws_server,
        'flowdiagram': "https://b3pflzry5l5wbaenwtdytiv7se0ykzkc" + aws_server,
        'customer_portal': "https://roxbi254sch3yijt7tqbz4s7jq0jxddr" + aws_server,
        'compliance_function': "https://srsybz6dbjz45skdwq6quou4ua0rxbnk" + aws_server,
        'customprocess': "https://7ntcvdqj4r23uklomzmeiwq7nq0dhblq" + aws_server,
        'analyze_function': "https://scqfjxbrko57bekv4lqkvu24fa0cmapi" + aws_server,
        'summarize': "https://tu5zdmjxvvzbzih6yytjtbm6fa0uvjba" + aws_server,
        'explain': "https://vdcg2nzj2jtzmtzzcmfwbvg4ey0jxghj" + aws_server,
        'testgen': "https://mqxkx5m7hehbskfvrcfwctbt7y0gghab" + aws_server,
        'generate': "https://egw2c7dn5vz3leffr3mfqodx3a0perwp" + aws_server,
    },
    'dev': {
        'analyze': "https://iyn66vkb6lmlcb4log6d3ah7d40axgqu.lambda-url.us-west-2.on.aws/",
        'codeguidelines': "https://4govp5ze7uyio3kjehtarpv24u0nabhw.lambda-url.us-west-2.on.aws/",
        'user_organizations': "https://cro3oyez4g56b33hvglfwytg3q0alxrz.lambda-url.us-west-2.on.aws/",
        'compliance': "https://q57gtrfpkuzquelgqtnncpjwta0nngfx.lambda-url.us-west-2.on.aws/",
        'blueprint': "https://67wxr6xq76bj5jiaoct5qjzble0wfmdt.lambda-url.us-west-2.on.aws/",
        'flowdiagram': "https://54t2jblqus2ou7letg3g2eph7y0aydtk.lambda-url.us-west-2.on.aws/",
        'customer_portal': "https://hry4lqp3ktulatehaowyzhkbja0mkjob.lambda-url.us-west-2.on.aws/",
        'compliance_function': "https://t4so4gqwf5rr5fr7pvlpytvkne0prvcv.lambda-url.us-west-2.on.aws/",
        'customprocess': "https://fudpixnolc7qohinghnum2nlm40wmozy.lambda-url.us-west-2.on.aws/",
        'analyze_function': "https://fubldwjkv4nau5qcnbrqilv6ba0dmkcc.lambda-url.us-west-2.on.aws/",
        'summarize': "https://sh6w6cyjee6wmtmlqutbxy6d2y0vaaas.lambda-url.us-west-2.on.aws/",
        'explain': "https://jorsb57zbzwcxcjzl2xwvah45i0mjuxs.lambda-url.us-west-2.on.aws/",
        'testgen': "https://gylbelpkobvont6vpxp4ihw5fm0iwnto.lambda-url.us-west-2.on.aws/",
        'generate': "https://ukkqda6zl22nd752blcqlv3rum0ziwnq.lambda-url.us-west-2.on.aws/",
    }
}


@app.lambda_function(name='monitor_user_organizations')
def monitor_user_organizations(event, _):
    results_test = {'organizations'}

    return test_api_status("user_organizations", service_uris[stage]['user_organizations'], None, results_test)


@app.lambda_function(name='monitor_customer_portal')
def monitor_customer_portal(event, _):
    results_test = {'status', 'portal_url'}
    return test_api_status("customer_portal", service_uris[stage]['customer_portal'], None, results_test)


@app.lambda_function(name='monitor_explain')
def monitor_explain(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'explanation', 'chunked', 'truncated'}
    return test_api_status("explain", service_uris[stage]['explain'], request_body, results_test)


@app.lambda_function(name='monitor_testgen')
def monitor_testgen(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'testcode', 'chunked', 'truncated'}
    return test_api_status("testgen", service_uris[stage]['testgen'], request_body, results_test)


key_IsChunked = 'chunked'


@app.lambda_function(name='monitor_summarize')
def monitor_summarize(event, _):
    request_body = {
        'inputs': 'first sentence\nsecond sentence\nthird sentence',
        'analysis_label': 'Explanation',
        'analysis_type': 'explain',
    }
    results_test = {'analysis_label', 'analysis_type', 'analysis', key_IsChunked, 'truncated'}
    response = test_api_status("summarize", service_uris[stage]['summarize'], request_body, results_test)

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
    response2 = test_api_status("summarize", service_uris[stage]['summarize'], request_body, results_test)
    return response if not response['statusCode'] == 200 or not response['isSuccessful'] or not response['functionalPass'] else response2


@app.lambda_function(name='monitor_flowdiagram')
def monitor_flowdiagram(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'analysis', 'chunked', 'truncated'}
    return test_api_status("flowdiagram", service_uris[stage]['flowdiagram'], request_body, results_test)


@app.lambda_function(name='monitor_analyze')
def monitor_analyze(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'analysis', 'chunked', 'truncated'}
    return test_api_status("analyze", service_uris[stage]['analyze'], request_body, results_test)


@app.lambda_function(name='monitor_analyze_function')
def monitor_analyze_function(event, _):
    request_body = {'code': 'print("Hello, World!")',
                    'inputMetadata': json.dumps({'lineNumberBase': 0})}
    results_test = {'status', 'details'}
    return test_api_status("analyze_function", service_uris[stage]['analyze_function'], request_body, results_test)


@app.lambda_function(name='monitor_compliance')
def monitor_compliance(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'analysis', 'chunked', 'truncated'}
    return test_api_status("compliance", service_uris[stage]['compliance'], request_body, results_test)


@app.lambda_function(name='monitor_compliance_function')
def monitor_compliance_function(event, _):
    request_body = {'code': 'print("Hello, World!")', 'inputMetadata': json.dumps({'lineNumberBase': 0})}
    results_test = {'status', 'details'}
    return test_api_status("compliance_function", service_uris[stage]['compliance_function'], request_body, results_test)


@app.lambda_function(name='monitor_blueprint')
def monitor_blueprint(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'blueprint', 'chunked', 'truncated'}
    return test_api_status("blueprint", service_uris[stage]['blueprint'], request_body, results_test)


@app.lambda_function(name='monitor_codeguidelines')
def monitor_codeguidelines(event, _):
    request_body = {'code': 'print("Hello, World!")'}
    results_test = {'analysis', 'chunked', 'truncated'}
    return test_api_status("codeguidelines", service_uris[stage]['codeguidelines'], request_body, results_test)


@app.lambda_function(name='monitor_generate')
def monitor_generate(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
        'explanation': 'This code is a simple hello world program.',
    }
    results_test = {'code', 'chunked', 'truncated'}
    return test_api_status("generate", service_uris[stage]['generate'], request_body, results_test)


@app.lambda_function(name='monitor_customprocess')
def monitor_customprocess(event, _):

    code = 'print("Hello, World!")'
    prompt = "Analyze this code to identify use of code incompatible with a commercial license, such as any open source license.\n\nExamples of licenses include BSD, MIT, GPL, LGPL, Apache or other licenses that may conflict with commercial licenses.\n\nFor any identified licenses in the code, provide online web links to relevant license analysis.\n\n\n" + code

    request_body = {'code': code, 'prompt': prompt}
    results_test = {'analysis', 'chunked', 'truncated'}

    response = test_api_status("customprocess", service_uris[stage]['customprocess'], request_body, results_test)

    this_role_system = "I am a sofware architect bot. I will analyze the code for architectural, algorithmic and design issues."
    request_body = {
        # 'code': code,
        # 'prompt': prompt,
        'messages': json.dumps([
            {
                "role": "system",
                "content": this_role_system
            },
            {
                "role": "user",
                "content": prompt
            }]),
    }
    response2 = test_api_status("customprocess", service_uris[stage]['customprocess'], request_body, results_test)

    return response if not response['statusCode'] == 200 \
        or not response['isSuccessful'] \
        or not response['functionalPass'] else response2
