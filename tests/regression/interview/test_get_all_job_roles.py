"""Mirrors tests/test_regression/test_interview/test_get_all_job_roles.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.get_all_job_roles
def test_get_all_job_roles(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_all_job_roles()
