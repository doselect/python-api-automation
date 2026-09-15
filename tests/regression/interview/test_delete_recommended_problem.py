"""
Mirrors tests/test_regression/test_interview/test_delete_recommended_problem.py (do-api-automation).
Source calls `delete_recommended_problem(auth_manager, shared_data)` — swapping the actual
(shared_data, problem_slug) signature's arguments (a call-site bug: `shared_data` becomes the
AuthManager object inside the function, `problem_slug` becomes the real shared_data dict) — moot
here since the fixture-based response handler takes no shared_data/auth_manager arguments at all.
"""
from __future__ import annotations

import pytest

from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.delete_recommended_problem
def test_delete_recommended_problem(interview_response_handler: InterviewResponseHandler):
    interview_response_handler.delete_recommended_problem()
