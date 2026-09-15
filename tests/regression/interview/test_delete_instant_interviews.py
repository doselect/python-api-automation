"""Mirrors tests/test_regression/test_interview/test_delete_instant_interviews.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
@pytest.mark.delete_instant_interviews
def test_delete_all_instant_interviews(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.delete_all_instant_interviews()
