"""Mirrors tests/test_regression/test_interview/test_get_interview_problem_setters.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.get_problem_setters
def test_get_problem_setters(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.get_problem_setters()
