import boto3
import argparse
from termcolor import colored


def list_all_canaries_status(stage=None, status=None, detailed=False):
    client = boto3.client('synthetics', region_name='us-west-2')  # Change the region name if needed
    failing_services = []
    not_running_services = []

    response = client.describe_canaries()

    for canary in response['Canaries']:
        if stage is None or canary['Name'].startswith(stage):
            # Get last run of the canary
            last_run_response = client.get_canary_runs(Name=canary['Name'], MaxResults=1)
            if last_run_response['CanaryRuns']:
                last_run = last_run_response['CanaryRuns'][0]
                canary_status = last_run['Status']['State']
                if status is None or canary_status.lower() == status.lower():
                    if canary_status == 'FAILED':
                        failing_services.append(canary['Name'])
                    elif canary_status != 'PASSED':
                        not_running_services.append(canary['Name'])

                    if detailed:
                        print(colored(f"Canary Name: {canary['Name']}", 'green' if canary_status == 'PASSED' else ('red' if canary_status == 'FAILED' else 'yellow')))
                        print(f"Canary Status: {canary_status}")
                        # Format the datetime
                        timestamp = last_run['Timeline']['Started']
                        formatted_timestamp = timestamp.strftime('%-I:%M%p')
                        print(f"Last Run Timestamp: {formatted_timestamp}")
                        print("-----")
            else:
                not_running_services.append(canary['Name'])

    if failing_services:
        print(colored("Failing Services are: " + ', '.join(failing_services), 'red'))
        return 1
    if not_running_services:
        print(colored("Services Not Running are: " + ', '.join(not_running_services), 'yellow'))
        return 1
    if not failing_services and not not_running_services:
        print(colored(f"All {len(response['Canaries'])} Services are Running and Passing", 'green'))
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check status of specific AWS canaries.')
    parser.add_argument('--stage', type=str, help='The stage used to filter canaries.')
    parser.add_argument('--status', type=str, help='The status used to filter canary runs.')
    parser.add_argument('--detailed', action='store_true', help='Print detailed information of each canary.')
    args = parser.parse_args()
    result = list_all_canaries_status(args.stage, args.status, args.detailed)

    exit(result)
