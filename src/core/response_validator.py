"""
Ports utils/validator.py from https://github.com/doselect/do-api-automation.git.

`validate_response_code` is the assertion helper used by (almost) every ported do-api-automation
test — same behavior as the source: assert the status code, and in PRODUCTION also feed the
failure-tracker (see src/core/failure_tracker.py) so repeatedly-flaky cases can be Teams-alerted.
"""
from __future__ import annotations

import json

from jsonschema import validate
from requests import Response

from src.core.do_api_config import ENVIRONMENT
from src.core.failure_tracker import log_failure, log_success


def validate_response_schema(response: dict, schema_file: str) -> None:
    """Mirrors utils.validator.validate_response_schema(response, schema_file)."""
    with open(f"schemas/{schema_file}", "r") as file:
        schema = json.load(file)
    validate(instance=response, schema=schema)


def validate_response_code(test_case_name: str, response: Response, expected_status_code: int) -> None:
    """Mirrors utils.validator.validate_response_code(test_case_name, response, expected_status_code)."""
    try:
        assert response.status_code == expected_status_code
        if ENVIRONMENT == "PRODUCTION":
            log_success(test_case_name)
    except AssertionError:
        if ENVIRONMENT == "PRODUCTION":
            log_failure(test_case_name)
        raise
