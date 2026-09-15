"""Mirrors tests/test_regression/test_interview/test_get_active_interviewers.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
def test_get_active_interviewers(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_active_interviewers()
