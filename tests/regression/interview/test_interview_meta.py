"""Mirrors tests/test_regression/test_interview/test_interview_meta.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.get_interview_meta
def test_get_interview_meta(interview_response_handler: InterviewResponseHandler):
    interview_token = interview_response_handler.get_or_create_fresh_token()
    interview_response_handler.get_interview_meta(interview_token)
    interview_response_handler.get_interview_meta(interview_token)
