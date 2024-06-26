
from chalicelib.telemetry import cloudwatch
from chalicelib.version import API_VERSION

import random
import time
import traceback
import requests
import os

service_name = 'boostCloudService'

# Define the directory where test data files are stored
DATA_DIR = "chalicelib/tests/data"

test_data_dir = os.path.join(os.path.abspath(os.path.curdir), DATA_DIR)


def load_all_files_to_map(directory):
    test_data = {}

    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, directory)

            with open(file_path, 'r') as file:
                content = file.read()

            test_data[relative_path] = content

    return test_data


test_data = load_all_files_to_map(test_data_dir)

# Example usage
# file_content = test_data['compliance/files.json']
# print(file_content)


def generateAuthSession():
    # Implement logic here to fetch github session and return it
    return 'testemail: boost-service-monitor@polytest.ai'


def eval_test_api_status(api, testurl, request_body, results_test):
    try:
        result = _test_api_status(api, testurl, request_body, results_test)

        print(f"API Test Result: {api} : {testurl} : {result}")
        return result

    except Exception:
        errorInfo = traceback.print_exc()
        print(f"Exception/Error: {api} : {testurl} : {errorInfo}")


def _test_api_status(api, testurl, request_body, results_test):
    headers = {'User-Agent': f'Boost-VSCE/{API_VERSION}'}

    session = generateAuthSession()
    payload = {"session": session, "organization": "polytest.ai"}

    # Merge request_body into payload
    if request_body:
        payload.update(request_body)

    max_retries = 3
    retries = 0
    json_response = None

    while retries <= max_retries:
        start_time = time.time()

        try:
            response = requests.post(testurl, headers=headers, json=payload)
            if response.status_code == 200:
                # Convert response to json
                json_response = response.json()

                # Verify all members of results_test are found in response and non-empty data
                for member in results_test:
                    if member not in json_response:
                        return {'error': f"Missing or empty data: {member}"}

                break
            elif response.status_code == 500:
                # Convert response to json
                json_response = response.json()

                if 'error' not in json_response:
                    return {'error': "Missing or empty data: error"}

                break
            else:
                try:
                    json_response = response.json()
                except Exception:
                    pass

        except Exception:
            response = {"statusCode": 500, "body": traceback.format_exc()}
            print(f"Exception/Error: {api} : {response['body']}")

        retries += 1
        if retries <= max_retries:
            # if running in AWS, just retry immediately (to save debugging time)
            if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
                time.sleep(random.uniform(15, 30))  # wait 15-30 seconds

    response_time = time.time() - start_time
    isSuccessful = float(1 if response.status_code == 200 else 0)
    duration = float("{:.3f}".format(response_time))

    functionalPass = float('error' not in json_response if json_response else False)
    if 'error' in json_response if json_response else False:
        print(f"Exception/Error: {api} : {json_response['error']}")

    if cloudwatch:
        # Publish response time metric
        cloudwatch.put_metric_data(MetricData=[
            {
                'MetricName': 'ResponseTime',
                'Dimensions': [
                    {
                        'Name': 'URL',
                        'Value': testurl
                    },
                    {
                        'Name': 'api',
                        'Value': api
                    },
                ],
                'Unit': 'Seconds',
                'Value': response_time
            },
        ], Namespace=service_name)

        # Publish status code metric
        cloudwatch.put_metric_data(MetricData=[
            {
                'MetricName': 'StatusCode',
                'Dimensions': [
                    {
                        'Name': 'URL',
                        'Value': testurl
                    },
                    {
                        'Name': 'api',
                        'Value': api
                    },
                ],
                'Unit': 'None',
                'Value': isSuccessful
            },
        ], Namespace=service_name)

        # Publish functional state
        cloudwatch.put_metric_data(MetricData=[
            {
                'MetricName': 'FunctionalPass',
                'Dimensions': [
                    {
                        'Name': 'URL',
                        'Value': testurl
                    },
                    {
                        'Name': 'api',
                        'Value': api
                    },
                ],
                'Unit': 'None',
                'Value': functionalPass
            },
        ], Namespace=service_name)

        # Publish failed retry metric
        if retries > 0 and isSuccessful:
            cloudwatch.put_metric_data(MetricData=[
                {
                    'MetricName': 'FailedRetry',
                    'Dimensions': [
                        {
                            'Name': 'URL',
                            'Value': testurl
                        },
                        {
                            'Name': 'api',
                            'Value': api
                        },
                    ],
                    'Unit': 'None',
                    'Value': (retries - 1)
                },
            ], Namespace=service_name)
    else:
        print(f"{service_name}: {api}: status={isSuccessful} : function={functionalPass} : {duration} sec")

    return {
        'statusCode': response.status_code,
        'responseTime': response_time,
        'isSuccessful': isSuccessful,
        'functionalPass': functionalPass,
        'retries': retries - 1,
        'payload': json_response  # add the json response to the returned data
    }
