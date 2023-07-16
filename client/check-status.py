import boto3
import argparse
from termcolor import colored

canary_schedule = "rate(1 hour)"
alarm_period = 3600  # 1 hour in seconds


def update_canary_schedule(client, debug, whatif, detailed, canary, new_schedule_expression=canary_schedule):
    canary_name = canary['Name']
    current_schedule = canary['Schedule']
    if current_schedule['Expression'] == new_schedule_expression:
        if debug:
            print(f"   Canary with the name {canary_name} already has the desired schedule.")
            print(f"      Schedule: {current_schedule}")
    else:
        if debug:
            print(f"   Updating canary with the name {canary_name} to have the desired schedule = 1 run/hour")
        if not whatif:
            try:
                response = client.update_canary(
                    Name=canary['Name'],
                    Schedule={
                        # Rate expressions are in 'rate(value unit)' format
                        'Expression': new_schedule_expression,
                        # Zero means that the canary is to run continuously
                        'DurationInSeconds': 0,
                    }
                )
                print(colored(f"   Canary with the name {canary_name} updated successfully.", 'yellow'))
                if debug:
                    print(f"   {response}")
            except client.exceptions.ResourceNotFoundException:
                print(colored(f"   Canary with the name {canary_name} not found.", "red"))
                return 1
            except Exception as e:
                print(colored(f"An error occurred: {e}", 'red'))
                return 1
        else:
            print(colored(f"   {canary_name}: Current schedule: {current_schedule['Expression']},"
                          f" but should be {new_schedule_expression}", 'red'))

            return 1

    return 0


def update_alarm(client, debug, whatif, canary_name):
    # Define alarm name based on canary name
    alarm_name = "Synthetics-Alarm-" + canary_name + "-1"

    # Check if alarm exists
    alarms = client.describe_alarms(AlarmNames=[alarm_name])
    if not alarms['MetricAlarms']:
        print(colored(f"   No Alarm with the name {alarm_name} found.", "red"))
        return False

    # Get the alarm
    alarm = alarms['MetricAlarms'][0]
    if alarm['Period'] == alarm_period:
        if debug:
            print(f"   Alarm for {canary_name} canary already has the desired period.")
        return True

    if debug:
        print(f"Alarm for {canary_name} canary:\n   {alarm}")

    if not whatif:
        # Update the alarm
        alarm_copy = alarm.copy()

        # Update the necessary fields in the copy
        alarm_copy['AlarmName'] = alarm_name
        alarm_copy['Period'] = alarm_period
        alarm_copy['ActionsEnabled'] = True
        del alarm_copy['AlarmArn']
        del alarm_copy['AlarmConfigurationUpdatedTimestamp']
        del alarm_copy['StateValue']
        del alarm_copy['StateReason']
        del alarm_copy['StateReasonData']
        del alarm_copy['StateUpdatedTimestamp']

        # Call the put_metric_alarm function with the updated dictionary
        client.put_metric_alarm(**alarm_copy)

        print(colored(f"   Alarm for Canary {canary_name} updated successfully.", 'yellow'))
    else:
        print(colored(f"   Alarm for Canary {canary_name} should be updated"
                      f" to have the following period: {alarm_period}", 'red'))
        return False

    return True


def list_all_canaries_status(client, debug, whatif, stage=None, status=None, detailed=False):
    failing_services = []
    not_running_services = []
    misconfigured_services = []

    response = client.describe_canaries()

    for canary in response['Canaries']:
        if stage is not None and not canary['Name'].startswith(stage):
            continue

        if debug:
            print(f"Canary Name: {canary['Name']}")

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
                    print(colored("   Status:",
                                  'green' if canary_status == 'PASSED' else
                                  ('red' if canary_status == 'FAILED' else 'yellow')))
                    # Format the datetime
                    timestamp = last_run['Timeline']['Started']
                    formatted_timestamp = timestamp.strftime('%-I:%M%p')
                    print(f"   Last Run Timestamp: {formatted_timestamp}")
                    print("-----")
        else:
            not_running_services.append(canary['Name'])

        if update_canary_schedule(client, debug, whatif, detailed, canary, canary_schedule) == 1:
            misconfigured_services.append(canary['Name'])

        # Update alarm schedule
        cw_client = boto3.client('cloudwatch', region_name='us-west-2')
        if not update_alarm(cw_client, debug, whatif, canary['Name']):
            misconfigured_services.append(canary['Name'])

    print("\n   ")

    if misconfigured_services:
        print(colored("Misconfigured Services are:\n  " + ',\n  '.join(misconfigured_services), 'red'))
        return 1
    if failing_services:
        print(colored("Failing Services are:\n  " + ',\n  '.join(failing_services), 'red'))
        return 1
    if not_running_services:
        print(colored("Services Not Running are:\n  " + ',\n  '.join(not_running_services), 'yellow'))
        return 1
    if not failing_services and not not_running_services:
        print(colored(f"All {len(response['Canaries'])} Services are Running and Passing", 'green'))
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check status of specific AWS canaries.')
    parser.add_argument('--stage', type=str, help='The stage used to filter canaries.')
    parser.add_argument('--debug', action='store_true', help='Enable Debug console logging.')
    parser.add_argument('--whatif', action='store_true', help='Check config = but do not update.')
    parser.add_argument('--status', type=str, help='The status used to filter canary runs.')
    parser.add_argument('--detailed', action='store_true', help='Print detailed information of each canary.')
    args = parser.parse_args()

    client = boto3.client('synthetics', region_name='us-west-2')  # Change the region name if needed

    try:
        result = list_all_canaries_status(client, args.debug, args.whatif, args.stage, args.status, args.detailed)
    except KeyboardInterrupt:
        print(colored("Exiting by User Interupt...", 'red'))
        result = 1

    exit(result)
