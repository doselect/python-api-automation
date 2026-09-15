"""Mirrors tests/test_regression/test_interview/test_get_job_role_details.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.get_job_role_details
def test_get_job_role_details(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_job_role_details()
