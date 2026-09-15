"""
Mirrors tests/public_apis/problems/conftest.py (do-api-automation): create_problem/lock_problem/
add_testcase fixtures, now going through ProblemsResponseHandler instead of api_helper directly.
`autouse=True` is preserved from the source even though each fixture only returns a factory
callable — the fixture body itself runs for every test in this folder, but no API call happens
unless a test explicitly invokes the returned closure.
"""
from __future__ import annotations

import pytest

from src.responses.problems_response_handler import ProblemsResponseHandler


@pytest.fixture(scope="function", autouse=True)
def create_problem(problems_response_handler: ProblemsResponseHandler):
    def _create_problem():
        payload = {
            "name": "Doselect API Problem",
            "problem_type": "SCR",
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
        return response.json().get("slug")

    return _create_problem


@pytest.fixture(scope="function", autouse=True)
def lock_problem(create_problem, problems_response_handler: ProblemsResponseHandler):
    def _lock_problem():
        problem_slug = create_problem()
        problems_response_handler.lock_problem(problem_slug)
        return problem_slug

    return _lock_problem


@pytest.fixture(scope="function", autouse=True)
def add_testcase(problems_response_handler: ProblemsResponseHandler):
    def _add_testcase(problem_slug):
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
        return response.json().get("id")

    return _add_testcase
