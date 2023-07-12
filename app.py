from chalice import Chalice
import os
import json

from chalicelib.app_utils import test_api_status

app = Chalice(app_name='boost-monitor')

aws_server = ".lambda-url.us-west-2.on.aws/"

# Determine the stage by checking the CHALICE_STAGE environment variable
stage = os.getenv('CHALICE_STAGE', 'local')

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
        'performance': "https://zr4gcodfteyi3zi5skcqnx2fge0rnjdk" + aws_server,
        'performance_function': "https://vhdpiji3mrr5ass7o5tx5mx5oa0nrjth" + aws_server,
        'compare_code': "https://h4vna4mvnun3jkfmoceobnnaau0drouk" + aws_server,

    },
    'dev': {
        'analyze': "https://iyn66vkb6lmlcb4log6d3ah7d40axgqu" + aws_server,
        'codeguidelines': "https://4govp5ze7uyio3kjehtarpv24u0nabhw" + aws_server,
        'user_organizations': "https://cro3oyez4g56b33hvglfwytg3q0alxrz" + aws_server,
        'compliance': "https://q57gtrfpkuzquelgqtnncpjwta0nngfx" + aws_server,
        'blueprint': "https://67wxr6xq76bj5jiaoct5qjzble0wfmdt" + aws_server,
        'flowdiagram': "https://54t2jblqus2ou7letg3g2eph7y0aydtk" + aws_server,
        'customer_portal': "https://hry4lqp3ktulatehaowyzhkbja0mkjob" + aws_server,
        'compliance_function': "https://t4so4gqwf5rr5fr7pvlpytvkne0prvcv" + aws_server,
        'customprocess': "https://fudpixnolc7qohinghnum2nlm40wmozy" + aws_server,
        'analyze_function': "https://fubldwjkv4nau5qcnbrqilv6ba0dmkcc" + aws_server,
        'summarize': "https://sh6w6cyjee6wmtmlqutbxy6d2y0vaaas" + aws_server,
        'explain': "https://jorsb57zbzwcxcjzl2xwvah45i0mjuxs" + aws_server,
        'testgen': "https://gylbelpkobvont6vpxp4ihw5fm0iwnto" + aws_server,
        'generate': "https://ukkqda6zl22nd752blcqlv3rum0ziwnq" + aws_server,
        'performance': "https://kh5r75yzyxe3idb223bei7tzni0vdyab" + aws_server,
        'performance_function': "https://6ucgf5nhzygxehglg5r7nd73640lykwa" + aws_server,
        'compare_code': "https://ztnhbmjlticv336bbmwlxsuphy0ctclu" + aws_server,
        'quick-blueprint': "https://c2m6d7mgrgypx3mzktbxoawfpa0acsja" + aws_server,
        'draft-blueprint': "https://b7zk2dm2haygvcluz4jx2by3vm0ypljn" + aws_server,
    },
    'local': {
        'analyze': "http://127.0.0.1:8000/analyze",
        'codeguidelines': "http://127.0.0.1:8000/codeguidelines",
        'user_organizations': "http://127.0.0.1:8000/user_organizations",
        'compliance': "http://127.0.0.1:8000/compliance",
        'blueprint': "http://127.0.0.1:8000/blueprint",
        'flowdiagram': "http://127.0.0.1:8000/flowdiagram",
        'customer_portal': "http://127.0.0.1:8000/customer_portal",
        'compliance_function': "http://127.0.0.1:8000/compliance_function",
        'customprocess': "http://127.0.0.1:8000/customprocess",
        'analyze_function': "http://127.0.0.1:8000/analyze_function",
        'summarize': "http://127.0.0.1:8000/summarize",
        'explain': "http://127.0.0.1:8000/explain",
        'testgen': "http://127.0.0.1:8000/testgen",
        'generate': "http://127.0.0.1:8000/generate",
        'performance': "http://127.0.0.1:8000/performance",
        'performance_function': "http://127.0.0.1:8000/performance_function",
        'compare_code': "http://127.0.0.1:8000/compare_code",
        'quick-blueprint': "http://127.0.0.1:8000/quick-blueprint",
        'draft-blueprint': "http://127.0.0.1:8000/draft-blueprint",
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


@app.lambda_function(name='monitor_performance')
def monitor_performance(event, _):
    request_body = {
        'code': 'print("Hello, World!")',
    }
    results_test = {'analysis', 'chunked', 'truncated'}
    return test_api_status("performance", service_uris[stage]['performance'], request_body, results_test)


@app.lambda_function(name='monitor_performance_function')
def monitor_performance_function(event, _):
    request_body = {'code': 'print("Hello, World!")', 'inputMetadata': json.dumps({'lineNumberBase': 0})}
    results_test = {'status', 'details'}
    return test_api_status("performance_function", service_uris[stage]['performance_function'], request_body, results_test)


@app.lambda_function(name='monitor_quick-blueprint')
def monitor_quick_blueprint(event, _):

    sampleBlueprint = "# Architectural Blueprint Summary for: {projectName}"
    "* Software Project Type: web app, server code, cloud web service, mobile app, shared library, etc."
    "* High-Level Summary: Short summary of software project in a 2-3 sentences"
    "* Software Principles: multi-threaded, event-driven, data transformation, server processing, client app code, etc"
    "* Data Storage: shared memory, disk, database, SQL vs NoSQL, non-persisted, data separated from code"
    "* Software Licensing: Commercial & Non-Commercial licenses, Open Source licenses (BSD, MIT, GPL, LGPL, Apache, etc.). Identify conflicting licenses."
    "* Security Handling: encrypted vs non-encrypted data, memory buffer management, shared memory protections, all input is untrusted or trusted"
    "* Performance characteristics: multi-threaded, non-blocking code, extra optimized, background tasks, CPU bound processing, etc."
    "* Software resiliency patterns: fail fast, parameter validation, defensive code, error logging, etc."
    "* Analysis of the architectural soundness and best practices: code is consistent with its programming language style, structure is consistent with its application or server framework"
    "* Architectural Problems Identified: coarse locks in multi-threaded, global and shared memory in library, UI in a non-interactive server, versioning fragility, etc."

    request_body = {
        'filelist': ['src/extension.ts',
                     'src/test/runTest.ts',
                     'src/test/suite/index.ts',
                     'src/test/suite/extension.test.ts',
                     'package.json'],
        'projectName': 'typescript-sample-extension',
        'projectFile': '{"devDependencies": {"axios": "^1.3.5" }}',
        'draftBlueprint': sampleBlueprint,
        'code': 'print("Hello, World!")'
    }

    results_test = {'blueprint', 'chunked', 'truncated'}
    return test_api_status("quick-blueprint", service_uris[stage]['quick-blueprint'], request_body, results_test)


@app.lambda_function(name='monitor_draft-blueprint')
def monitor_draft_blueprint(event, _):
    request_body = {
        'filelist': ['src/extension.ts',
                     'src/test/runTest.ts',
                     'src/test/suite/index.ts',
                     'src/test/suite/extension.test.ts',
                     'package.json'],
        'projectName': 'typescript-sample-extension',
    }

    results_test = {'status', 'details'}
    return test_api_status("draft-blueprint", service_uris[stage]['draft-blueprint'], request_body, results_test)


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
