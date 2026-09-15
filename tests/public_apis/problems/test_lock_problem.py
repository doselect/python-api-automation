"""Mirrors tests/public_apis/problems/test_lock_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_lock_problem(create_problem, problems_response_handler: ProblemsResponseHandler, request):
    problem_slug = create_problem()

    response = problems_response_handler.lock_problem(problem_slug)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
