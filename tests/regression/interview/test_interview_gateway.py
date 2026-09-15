"""Mirrors tests/test_regression/test_interview/test_interview_gateway.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
@pytest.mark.interview_gateway
def test_interview_gateway(interview_response_handler: InterviewResponseHandler):
    interview_token = interview_response_handler.get_or_create_fresh_token()
    interview_response_handler.get_interview_gateway(interview_token)
