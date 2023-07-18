import argparse
import boto3
import requests
from termcolor import colored


def get_monitor_names(stage=None):
    monitor_names = set()  # Store monitor names in a set to exclude duplicates
    client = boto3.client('lambda', region_name='us-west-2')

    if stage == "all":
        stages = ["dev", "test", "prod"]
    else:
        stages = [stage]

    paginator = client.get_paginator('list_functions')

    for stage in stages:
        response_iterator = paginator.paginate(
            FunctionVersion='ALL',
            PaginationConfig={
                'PageSize': 50  # Adjust the page size as needed
            }
        )

        for response in response_iterator:
            functions = response['Functions']
            for function in functions:
                function_name = function['FunctionName']
                if function_name.startswith(f"boost-monitor-{stage}-monitor"):
                    # Store the full function name and URI for each stage
                    monitor_names.add((function_name, stage))

    return monitor_names  # Return the set of (function_name, stage) tuples


def test_monitors(stage=None, name=None, show_available=False):
    if show_available:
        monitors = get_monitor_names(stage=stage)
        print("Available monitor names:")
        deduped_monitors = set()
        for function_name, _ in monitors:
            # Extract the user-friendly name from the function name
            monitor_name = function_name.split('_', 1)[1]
            deduped_monitors.add(monitor_name)
        for monitor in deduped_monitors:
            if name in monitor or name is None:
                print(f"   {monitor}")
        return 0

    else:
        monitors = get_monitor_names(stage=stage)

        # Filter monitors based on name
        if name:
            monitors = [(function_name, stage) for function_name, stage in monitors if name in function_name]

        success = True
        failed = []
        all = 0
        # Run the monitors
        for function_name, stage in monitors:
            # Extract the user-friendly name from the function name
            monitor_name = function_name.split('_', 1)[1]

            # Retrieve the URI for the monitor
            client = boto3.client('lambda', region_name='us-west-2')
            config = client.get_function_url_config(FunctionName=function_name)
            uri = config['FunctionUrl']

            print(f"Running monitor: {monitor_name} in Stage:{stage}")
            all = all + 1
            response = requests.get(uri)
            if response.status_code == 200:
                print(colored(f"   {monitor_name}:PASSED", 'green'))
            else:
                success = False
                print(colored(f"   {monitor_name}:FAILED", 'red'))
                failed.append(f"{stage}:{monitor_name}")

        if success:
            print(colored(f"All {all} Tests PASSED", 'green'))
        else:
            print(colored(f"{len(failed)} Tests FAILED out of {all}", 'red'))
        return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run service monitors.")
    parser.add_argument("--stage", default="all", help="Specify the stage of the monitors.")
    parser.add_argument("--name", help="Specify the name of the monitor.")
    parser.add_argument("--showAvailable", action="store_true", help="Show available monitor names.")

    args = parser.parse_args()

    result = test_monitors(stage=args.stage, name=args.name, show_available=args.showAvailable)
    exit(result)
