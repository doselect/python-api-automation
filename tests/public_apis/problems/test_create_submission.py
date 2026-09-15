"""Mirrors tests/public_apis/problems/test_create_submission.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_create_submission(create_problem, problems_response_handler: ProblemsResponseHandler, request):
    problem_slug = create_problem()
    payload = {
        "technology": "python2",
        "problem_type": "SCR",
        "code": "print 'Hello World'",
        "email": "john@example.com",
        "problem_slug": f"{problem_slug}",
    }

    response = problems_response_handler.create_submission(payload)
    validate_response_code(request.node.name, response, 201)
    # Add more assertions based on expected response
