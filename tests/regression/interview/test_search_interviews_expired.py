"""Mirrors tests/test_regression/test_interview/test_search_interviews_expired.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_search_expired_interviews(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.search_interviews_based_on_status(status="EXPIRED")
