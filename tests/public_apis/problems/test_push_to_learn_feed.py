"""Mirrors tests/public_apis/problems/test_push_to_learn_feed.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_push_to_learn_feed(create_problem, problems_response_handler: ProblemsResponseHandler, request):
    problem_slug = create_problem()

    response = problems_response_handler.push_to_learn_feed(problem_slug)
    validate_response_code(request.node.name, response, 201)
    # Add more assertions based on expected response
