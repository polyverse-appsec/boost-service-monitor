import boto3
import argparse
from termcolor import colored
import datetime

secs_per_min = 60
secs_per_hour = 60 * secs_per_min
canary_schedule_hourly = "rate({} hour)"
canary_schedule_day = "cron(0 0 * * ? *)"
canary_schedule_cron = "cron(0 */{} * * ? *)"
alarm_period_ring_0 = 1  # primary user operations should be checked hourly
alarm_period_ring_1 = 3  # basic project functions should be checked every 3 hours
alarm_period_ring_2 = 6  # advanced project functions should be checked every 6 hours
alarm_period_ring_3 = 12  # basic cell/code level functions should be checked every 12 hours
alarm_period_ring_4 = 24  # advanced cell/code level functions should be checked every 24 hours

ring_0 = ['cust-portal', 'user-orgs', 'customer_portal']
ring_1 = ['analyze-func', 'compliance-func', 'perf-function', 'customprocess', 'draft-blueprint', 'explain', 'flowdiagram', 'quick-blueprint']
ring_2 = ['blueprint', 'summary']
ring_3 = ['analyze', 'compliance', 'perf']
ring_4 = ['codeguidelines', 'generate', 'testgen']


def update_canary_schedule(client, debug, whatif, detailed, canary, new_schedule_expression):
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


def get_alarms_by_substring(client, substring):
    alarms = []
    next_token = None

    while True:
        if next_token:
            response = client.describe_alarms(NextToken=next_token)
        else:
            response = client.describe_alarms()

        for alarm in response['MetricAlarms']:
            # extra heuristic check to make sure we don't mismatch substrings
            if substring in alarm['AlarmName'] and (("-func" in substring) == ("-func" in alarm['AlarmName'])):
                alarms.append(alarm)

        next_token = response.get('NextToken')
        if not next_token:
            break

    return alarms


def update_alarm(client, debug, whatif, stage, alarm_name, alarm_schedule, alarm_period, deleteDisabled) -> bool:

    if "summ" in alarm_name:
        print(colored(f"   Scanning Summarization Alarm {alarm_name}", 'yellow'))

    alarms = get_alarms_by_substring(client, alarm_name)

    # add monitor alarms as well as direct service alarms
    if stage is not None:
        monitor_name_fixup = alarm_name.replace(f"{stage}-", f"{stage}-monitor_")
        monitor_alarms = get_alarms_by_substring(client, monitor_name_fixup)

        alarms.extend(monitor_alarms)

    syntheticFound = False
    applicationInsightFound = True
    updatedRequired = False

    for alarm in alarms:

        # Update the alarm
        alarm_copy = alarm.copy()

        if alarm['AlarmName'].startswith("Synthetics-Alarm-" + alarm_name):
            syntheticFound = True

            if alarm['Period'] != alarm_period or not alarm['ActionsEnabled']:
                updatedRequired = True
            else:
                if debug:
                    print(f"   Alarm for {alarm_name} already has the desired config.")
                if not deleteDisabled:
                    continue

            if debug:
                print(f"Alarm for {alarm_name}:\n   {alarm}")

            if alarm_copy['Period'] != alarm_period:
                print(colored(f"   Alarm for {alarm_name} Period expected:{alarm_period} - actual:{alarm_copy['Period']}", 'red'))

                if whatif:
                    print(colored(f"   Alarm for {alarm_name} should be updated"
                                  f" to have the following period: {alarm_period}", 'red'))
                    continue

                alarm_copy['Period'] = alarm_period

            if not alarm_copy['ActionsEnabled']:
                print(colored(f"   Alarm for {alarm_name} ActionsEnabled expected:True - actual:{alarm_copy['ActionsEnabled']}", 'red'))

                if whatif:
                    print(colored(f"   Alarm for {alarm_name} should be updated"
                                  f" to have the ActionsEnabled True", 'red'))
                    continue

                alarm_copy['ActionsEnabled'] = True

            print(colored(f"   Synthetic Alarm for {alarm_name} updated successfully.", 'yellow'))

        elif alarm['AlarmName'].startswith("ApplicationInsights"):
            applicationInsightFound = True

            if alarm['ActionsEnabled']:
                if debug:
                    print(f"   Alarm for Application Insight {alarm['AlarmName']} is enabled (should be Disabled).")
                updatedRequired = True
            else:
                if debug:
                    print(f"   Alarm for Application Insight {alarm['AlarmName']} is disabled (as expected).")
                if not deleteDisabled:
                    continue

            if debug:
                print(f"Alarm for {alarm['AlarmName']} Application Insight:\n   {alarm}")

            if whatif:
                print(colored(f"   Alarm for Application Insight {alarm['AlarmName']} should be updated"
                              f" to have ActionsEnabled=False", 'red'))
                continue

            alarm_copy['ActionsEnabled'] = False

            # Dimensions is being returned along with metrics, but this is invalid
            #   combination for setting the alarm data
            del alarm_copy['Dimensions']

            print(colored(f"   Application Insight Alarm for {alarm['AlarmName']} Disabled successfully.", 'yellow'))

        else:
            print(colored(f"   Unexpected Alarm {alarm['AlarmName']} found and not handled", 'yellow'))
            continue

        # delete data not relevant to alarm config
        del alarm_copy['AlarmArn']
        del alarm_copy['AlarmConfigurationUpdatedTimestamp']

        # delete temporary state from past runs
        del alarm_copy['StateValue']
        del alarm_copy['StateReason']
        del alarm_copy['StateReasonData']
        del alarm_copy['StateUpdatedTimestamp']

        if deleteDisabled and not alarm_copy['ActionsEnabled']:
            print(colored(f"   Deleting Alarm {alarm['AlarmName']} as it is disabled.", 'yellow'))
            client.delete_alarms(AlarmNames=[alarm['AlarmName']])
            continue

        # Call the put_metric_alarm function with the updated dictionary
        client.put_metric_alarm(**alarm_copy)

    # Check if alarm exists
    if not syntheticFound:
        if debug:
            print(colored(f"   No Synthentic Alarm with the name {alarm_name} found.", "red"))

    if not applicationInsightFound:
        print(colored(f"   No Application Insights Alarms with the name {alarm_name} found.", "red"))

    return updatedRequired


def get_canaries_by_substring(client, substring=None):
    canaries = []
    next_token = None

    while True:
        if next_token:
            response = client.describe_canaries(NextToken=next_token)
        else:
            response = client.describe_canaries()

        for canary in response['Canaries']:
            if substring in canary['Name'] if substring else True:
                canaries.append(canary)

        next_token = response.get('NextToken')
        if not next_token:
            break

    return canaries


def check_status_of_all_canaries_and_alarms(client, debug, whatif, stage=None, name=None, status=None, detailed=False, useServerTime=False, deleteDisabled=False, checkAll=False):
    failing_services = []
    not_running_services = []
    misconfigured_services = []

    print("Checking all canaries...")

    canaries = get_canaries_by_substring(client)

    for canary in canaries:
        if stage is not None and not canary['Name'].startswith(stage):
            continue

        if name is not None and name not in canary['Name']:
            continue

        print(f"Checking: {canary['Name']}")

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
                    print(colored(f"   Status: {canary_status}",
                                  'green' if canary_status == 'PASSED' else
                                  ('red' if canary_status == 'FAILED' else 'yellow')))

                    timestamp = last_run['Timeline']['Started']

                    if useServerTime:
                        formatted_timestamp = timestamp.strftime('%-I:%M%p')
                    else:
                        local_timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo

                        utc_timestamp = datetime.datetime.strptime(timestamp.isoformat(), "%Y-%m-%dT%H:%M:%S.%f%z")
                        local_timestamp = utc_timestamp.astimezone(local_timezone)
                        formatted_timestamp = local_timestamp.strftime('%-I:%M%p')

                    print(f"   Last Run Timestamp: {formatted_timestamp}")
                    print("-----")
        else:
            not_running_services.append(canary['Name'])

        service_name = canary['Name'].replace(f"{stage}-", "", 1)

        if service_name in ring_0:
            this_alarm_period = alarm_period_ring_0
        elif service_name in ring_1:
            this_alarm_period = alarm_period_ring_1
        elif service_name in ring_2:
            this_alarm_period = alarm_period_ring_2
        elif service_name in ring_3:
            this_alarm_period = alarm_period_ring_3
        elif service_name in ring_4:
            this_alarm_period = alarm_period_ring_4
        else:
            print(colored(f"   Canary {canary['Name']} not in any ring", 'red'))
            continue

        if this_alarm_period == 24:
            desired_schedule = canary_schedule_day.format(this_alarm_period)
        elif this_alarm_period == 1:
            desired_schedule = canary_schedule_hourly.format(this_alarm_period)
        else:
            desired_schedule = canary_schedule_cron.format(this_alarm_period)

        if update_canary_schedule(client, debug, whatif, detailed, canary, desired_schedule) == 1:
            misconfigured_services.append(canary['Name'])

        # Update alarm schedule
        cw_client = boto3.client('cloudwatch', region_name='us-west-2')
        desired_period = this_alarm_period * secs_per_hour
        if update_alarm(cw_client, debug, whatif, stage, canary['Name'], desired_schedule, desired_period, deleteDisabled):
            misconfigured_services.append(canary['Name'])

        # special case customer portal naming variants
        if ('cust-portal' in canary['Name']):
            alarm_name = canary['Name'].replace("cust-portal", "customer_portal")
            if update_alarm(cw_client, debug, whatif, stage, alarm_name, desired_schedule, desired_period, deleteDisabled):
                misconfigured_services.append(canary['Name'])

        # special case summary naming variants
        if ('summary' in canary['Name']):
            alarm_name = canary['Name'].replace("summary", "summarize")
            if update_alarm(cw_client, debug, whatif, stage, alarm_name, desired_schedule, desired_period, deleteDisabled):
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
        print(colored(f"All {len(canaries)} Services are Running and Passing", 'green'))
        return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check status of specific AWS canaries.')
    parser.add_argument('--stage', type=str, help='The stage used to filter canaries.')
    parser.add_argument('--name', type=str, help='The name used to filter canaries.')
    parser.add_argument('--debug', action='store_true', help='Enable Debug console logging.')
    parser.add_argument('--deleteDisabled', action='store_true', help='Delete disabled alarms.')
    parser.add_argument('--whatif', action='store_true', help='Check config = but do not update.')
    parser.add_argument('--checkAll', action='store_true', help='Check all canaries and alarms, regardless of type')
    parser.add_argument('--status', type=str, help='The status used to filter canary runs.')
    parser.add_argument('--useServerTime', action='store_true', help='Print timestamps in Cloud server time (instead of local time).')
    parser.add_argument('--detailed', action='store_true', help='Print detailed information of each canary.')
    args = parser.parse_args()

    client = boto3.client('synthetics', region_name='us-west-2')  # Change the region name if needed

    try:
        result = check_status_of_all_canaries_and_alarms(client, args.debug, args.whatif, args.stage, args.name, args.status, args.detailed, args.useServerTime, args.deleteDisabled, args.checkAll)
    except KeyboardInterrupt:
        print(colored("Exiting by User Interupt...", 'red'))
        result = 1

    exit(result)
