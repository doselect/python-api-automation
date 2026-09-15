"""Mirrors tests/test_regression/test_interview/test_schedule_interview.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
@pytest.mark.interview_schedule
def test_schedule_interview(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_schedule_interview()
    interview_response_handler.post_cancel_interview()
