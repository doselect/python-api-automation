"""Mirrors tests/public_apis/problems/test_get_submission_ofproblem_byuser.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL_SUBMISSION, PROBLEM_SLUG
from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_get_submission_ofproblem_byuser(problems_response_handler: ProblemsResponseHandler, request):
    response = problems_response_handler.get_submission_of_problem_by_user(
        PROBLEM_SLUG, CANDIDATE_EMAIL_SUBMISSION
    )
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
