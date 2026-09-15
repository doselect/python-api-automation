"""Mirrors tests/public_apis/problems/test_unlock_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_unlock_problem(lock_problem, problems_response_handler: ProblemsResponseHandler, request):
    problem_slug = lock_problem()

    response = problems_response_handler.unlock_problem(problem_slug)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
