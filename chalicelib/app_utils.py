
from chalicelib.telemetry import cloudwatch
from chalicelib.version import API_VERSION

import random
import time
import traceback
import requests

service_name = 'boostCloudService'


def test_api_status(api, testurl):
    headers = {'User-Agent': f'Boost-VSCE/{API_VERSION}'}

    session = generateAuthSession()
    payload = {"session": session}

    max_retries = 3
    retries = 0
    while retries <= max_retries:
        start_time = time.time()

        try:
            response = requests.post(testurl, headers=headers, json=payload)
            if response.status_code == 200:
                break
        except Exception:
            response = {"statusCode": 500, "body": traceback.format_exc()}

        retries += 1
        if retries <= max_retries:
            time.sleep(random.uniform(15, 30))  # wait 15-30 seco

    response_time = time.time() - start_time
    isSuccessful = 1 if response.status_code == 200 else 0
    duration = float("{:.3f}".format(response_time))

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
                    'Value': retries
                },
            ], Namespace=service_name)
    else:
        print(f"{service_name}:{api}:status={isSuccessful}:{duration} sec")

    return {
        'statusCode': response.status_code,
        'responseTime': response_time,
        'isSuccessful': isSuccessful,
        'retries': retries
    }


def generateAuthSession():
    # Implement logic here to fetch github session and return it
    return 'testemail: boost-service-monitor@polytest.ai'
