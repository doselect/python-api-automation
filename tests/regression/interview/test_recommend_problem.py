"""Mirrors tests/test_regression/test_interview/test_recommend_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.interview_regression
def test_recommend_problem(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.post_recommend_problem()
