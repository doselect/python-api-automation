"""Mirrors tests/public_apis/problems/test_create_testcase_ofproblem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_create_testcase_ofproblem(
    create_problem, problems_response_handler: ProblemsResponseHandler, request
):
    problem_slug = create_problem()
    payload = {
        "name": "test case API 3",
        "input": "1",
        "output": "3",
        "is_sample": False,
        "weight": 2,
        "positive_annotation": "If this test case passes, the code handles null values properly",
        "negative_annotation": "If this test case passes, the code does not handles null values properly",
        "code": "",
        "score": 50,
        "penalty": 5,
    }

    response = problems_response_handler.add_testcase(problem_slug, payload)
    validate_response_code(request.node.name, response, 201)
    # Add more assertions based on expected response
