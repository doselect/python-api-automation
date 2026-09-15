"""Mirrors tests/test_regression/test_interview/test_clone_jobrole.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.clone_job_role
def test_clone_job_role(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_clone_job_role()
