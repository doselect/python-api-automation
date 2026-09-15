"""Mirrors tests/test_regression/test_interview/test_add_problem_during_interview.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
@pytest.mark.add_problem_during_interview
def test_search_problems(interview_response_handler: InterviewResponseHandler):
    search_response = interview_response_handler.get_search_problems()
    first_problem_details = search_response.json()["results"][0]
    interview_response_handler.post_add_problem_during_interview(first_problem_details=first_problem_details)
