"""Mirrors tests/test_regression/test_interview/test_search_problems.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_search_problems(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_search_problems()
