"""Mirrors tests/test_regression/test_interview/test_archieve_jobrole.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.archieve_job_role
def test_clone_job_role(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_archieve_job_role()
    interview_response_handler.get_all_job_roles()
