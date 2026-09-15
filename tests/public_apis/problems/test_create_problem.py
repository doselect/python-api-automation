"""Mirrors tests/public_apis/problems/test_create_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.response_validator import validate_response_code
from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.mark.public
def test_create_problem(problems_response_handler: ProblemsResponseHandler, request):
    payload = {
        "name": "Doselect API Problem",
        "problem_type": "PRJ",
        "time_limit_secs": 10,
        "tags": ["Regex"],
        "insight_tags": ["Python2"],
        "description": "This is not the problem you are looking for",
        "max_submissions": 5,
        "score": 75,
        "penalty": 1,
        "solving_time": "5",
        "stubs": {
            "python2": "print 'hello world'",
            "java7": "System.out.println('hello world')",
            "java": "System.out.println('hello world')",
        },
        "sample_solutions": {"python2": "def add(a,b): return a + b"},
        "technologies": ["python2", "java7", "lua"],
    }

    response = problems_response_handler.create_problem(payload)
    validate_response_code(request.node.name, response, 201)
    # Add more assertions based on expected response
