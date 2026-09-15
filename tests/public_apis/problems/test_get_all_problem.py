"""Mirrors tests/public_apis/problems/test_get_all_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_get_all_problems(problems_response_handler: ProblemsResponseHandler, request):
    response = problems_response_handler.get_all_problems()
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
