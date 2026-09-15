"""
Ports utils/config.py + the `get_csv_data` half of utils/generic_helpers.py from
https://github.com/doselect/do-api-automation.git.

Separate from file_io_utils.py's config.properties system (which the Salary Data API port reads
BaseURL from) — the do-api-automation suite configures itself entirely from environment variables
plus one CSV file of per-environment test data, so this module mirrors that scheme as-is rather
than forcing it through the properties-file reader.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path
from typing import Optional

# python-api-automation/src/core/do_api_config.py -> repo root is 2 parents up from this file's dir.
_REPO_ROOT = Path(__file__).resolve().parents[2]
# Mirrors resources/data/data.csv (Java... no wait, do-api-automation) — byte-for-byte copy.
DATA_FILE = _REPO_ROOT / "tests" / "data" / "do_api_automation" / "data.csv"

HEADERS = {"Content-Type": "application/json"}
TOKEN: Optional[str] = None  # Will be set dynamically, mirrors utils.config.TOKEN

BASE_URL = os.environ.get("BASE_URL")
DOSELECT_API_KEY = os.environ.get("DOSELECT_API_KEY")
DOSELECT_API_SECRET = os.environ.get("DOSELECT_API_SECRET")
FN_COMPANY_SLUG = os.environ.get("FN_COMPANY_SLUG")
FN_API_KEY = os.environ.get("FN_API_KEY")
FN_API_SECRET = os.environ.get("FN_API_SECRET")
BASE_URL_NON_API = os.environ.get("BASE_URL_NON_API")
ENVIRONMENT = os.environ.get("ENVIRONMENT")
TEAMS_WEBHOOK_URL = os.environ.get("TEAMS_WEBHOOK_URL")
DOSELECT_PRIMARY_DOMAIN = os.environ.get("DOSELECT_PRIMARY_DOMAIN")
DO_INTERVIEW_INTERFACE_DOMAIN = os.environ.get("DO_INTERVIEW_INTERFACE_DOMAIN")
DO_TEST_INTERFACE_DOMAIN = os.environ.get("DO_TEST_INTERFACE_DOMAIN")
INTERVIEW_APP_DOMAIN = os.environ.get("INTERVIEW_APP_DOMAIN")
AUTH_URL = os.environ.get("AUTH_URL")
RECRUITER_EMAIL = os.environ.get("RECRUITER_EMAIL")
ACCOUNT_TYPE = os.environ.get("ACCOUNT_TYPE", "recruiter")
PRODUCT_TYPE = os.environ.get("PRODUCT_TYPE", "doselect")
RECRUITER_USERNAME = os.environ.get("RECRUITER_USERNAME")
RECRUITER_PASSWORD = os.environ.get("RECRUITER_PASSWORD")
CANDIDATE_EMAIL_FOR_INVITE = os.environ.get("CANDIDATE_EMAIL_FOR_INVITE")
REPORT_SENDER_EMAIL = os.environ.get("REPORT_SENDER_EMAIL")
REPORT_SENDER_PASSWORD = os.environ.get("REPORT_SENDER_PASSWORD")
DOLORES_BASE_URL = os.environ.get("DOLORES_BASE_URL")
RECRUITER_ID = os.environ.get("RECRUITER_ID")
WEBSOCKET_DOMAIN = os.environ.get("WEBSOCKET_DOMAIN")
CREATOR_USERNAME = os.environ.get("CREATOR_USERNAME")
CREATOR_PASSWORD = os.environ.get("CREATOR_PASSWORD")
CREATOR_EMAIL = os.environ.get("CREATOR_EMAIL")
REVIEWER_USERNAME = os.environ.get("REVIEWER_USERNAME")
REVIEWER_PASSWORD = os.environ.get("REVIEWER_PASSWORD")
REVIEWER_EMAIL = os.environ.get("REVIEWER_EMAIL")
MODERATOR_USERNAME = os.environ.get("MODERATOR_USERNAME")
MODERATOR_PASSWORD = os.environ.get("MODERATOR_PASSWORD")
MODERATOR_EMAIL = os.environ.get("MODERATOR_EMAIL")
AUTOMATION_EMAIL = os.environ.get("AUTOMATION_EMAIL")
AUTOMATION_PASSWORD = os.environ.get("AUTOMATION_PASSWORD")

USER_TYPE_RECRUITER = "recruiter"
USER_TYPE_CANDIDATE = "hacker"
USER_TYPE_INTERVIEWER = "interviewer"
USER_TYPE_CREATOR = "content_creator"
USER_TYPE_REVIEWER = "reviewer"


def get_csv_data(key: str, environment: str) -> str:
    """
    Mirrors utils.generic_helpers.get_csv_data(key, environment): 'key' is matched against the
    first column of tests/data/do_api_automation/data.csv, 'environment' against the header row,
    and the corresponding cell is returned.
    """
    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)

            if not data:
                return "Error: CSV file is empty"

            headers = data[0]
            if environment not in headers:
                return f"Error: Environment '{environment}' not found"

            env_col = headers.index(environment)
            for row in data[1:]:
                if row and row[0] == key:
                    return row[env_col] if len(row) > env_col else ""

        return f"Error: Key '{key}' not found"
    except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
        return f"Error: {e}"


TEST_SLUG_RECRUIT = get_csv_data("TEST_SLUG_RECRUIT", ENVIRONMENT)
CANDIDATE_EMAIL = get_csv_data("CANDIDATE_EMAIL", ENVIRONMENT)
CANDIDATE_USERNAME = get_csv_data("CANDIDATE_USERNAME", ENVIRONMENT)
CANDIDATE_EMAIL_SUBMISSION = get_csv_data("CANDIDATE_EMAIL_SUBMISSION", ENVIRONMENT)
TEST_SLUG_LEARN = get_csv_data("TEST_SLUG_LEARN", ENVIRONMENT)
PROBLEM_SLUG = get_csv_data("PROBLEM_SLUG", ENVIRONMENT)
ACCESS_CODE_FOR_REPORT = get_csv_data("ACCESS_CODE_FOR_REPORT", ENVIRONMENT)
SOLUTION_SLUG = get_csv_data("SOLUTION_SLUG", ENVIRONMENT)
UI_UX_SOLUTION_SLUG = get_csv_data("UI_UX_SOLUTION_SLUG", ENVIRONMENT)
FN_TEST_SLUG = get_csv_data("FN_TEST_SLUG", ENVIRONMENT)
DOSELECT_COMPANY_SLUG = get_csv_data("DOSELECT_COMPANY_SLUG", ENVIRONMENT)
PROCTORING_TEST_SLUG = get_csv_data("PROCTORING_TEST_SLUG", ENVIRONMENT)
FN_HTML_REPORT_TRANSCRIPT_ID = get_csv_data("FN_HTML_REPORT_TRANSCRIPT_ID", ENVIRONMENT)
FN_BULK_HTML_TRANSCRIPT_ID = get_csv_data("FN_BULK_HTML_TRANSCRIPT_ID", ENVIRONMENT)
CANDIDATE_USERNAME_FOR_SOLUTIONSET = get_csv_data("CANDIDATE_USERNAME_FOR_SOLUTIONSET", ENVIRONMENT)
SOLUTIONSET_ID = get_csv_data("SOLUTIONSET_ID", ENVIRONMENT)
CANDIDATE_EMAIL_INTERVIEW = get_csv_data("CANDIDATE_EMAIL_INTERVIEW", ENVIRONMENT)
CONTEST_ID = get_csv_data("CONTEST_ID", ENVIRONMENT)
