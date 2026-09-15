"""Mirrors tests/test_regression/test_interview/test_create_new_instant_link.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.create_instant_link
def test_create_new_instant_link(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_or_create_fresh_token(force_refresh=True)
