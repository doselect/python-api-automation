"""Mirrors tests/public_apis/problems/test_update_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_update_problem(create_problem, problems_response_handler: ProblemsResponseHandler, request):
    problem_slug = create_problem()
    payload = {
        "name": "Updated Problem Name",
        "tags": ["Java"],
        "description": "A new description of the problem",
        "max_submissions": 10,
        "solving_time": "5",
    }

    response = problems_response_handler.update_problem(problem_slug, payload)
    validate_response_code(request.node.name, response, 202)
    # Add more assertions based on expected response
