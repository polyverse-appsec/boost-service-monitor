import sys
import os

if not ('AWS_CHALICE_CLI_MODE' not in os.environ and 'AWS_LAMBDA_FUNCTION_NAME' in os.environ):

    # Determine the parent directory's path.
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    # Append the parent directory to sys.path.
    sys.path.append(parent_dir)

# flake8: noqa
import json
from chalicelib.app_utils import eval_test_api_status, test_data
from chalicelib.server_utils import service_uris, stage


# examples of high-severity analysis in json
sample_analysis_json = test_data['quick-summary/severity_analysis.json']

# high-level categorization of severities and categories in json
categorizations_json = test_data['quick-summary/categorizations.json']

filelist_json = test_data['quick-summary/files.json']


def test_quick_summary():
    projectFileList = json.loads(filelist_json)

    request_body = {
        'filelist': projectFileList,
        'examples': sample_analysis_json,
        'issue_categorization': categorizations_json,
    }

    results_test = {'summary', 'truncated', 'chunked'}
    response = eval_test_api_status("quick-summary", service_uris[stage]['quick-summary'], request_body, results_test)

    # function creates details from an embedded JSON string
    summary = response['payload']['summary']
    lower_summary = summary.lower()

    print("\n\n" + summary + "\n\n\n\n")

    assert '395' in lower_summary
    assert 'risk' in lower_summary
    assert 'impact' in lower_summary
    assert 'gdpr' in lower_summary
    assert 'hipaa' in lower_summary
    assert 'hardcoded' in lower_summary

    return response
