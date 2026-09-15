"""Mirrors tests/public_apis/problems/test_delete_testcase_ofproblem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_delete_testcase_ofproblem(
    create_problem, add_testcase, problems_response_handler: ProblemsResponseHandler, request
):
    problem_slug = create_problem()
    testcase_id = add_testcase(problem_slug)

    response = problems_response_handler.delete_testcase(problem_slug, testcase_id)
    validate_response_code(request.node.name, response, 204)
    # Add more assertions based on expected response
