"""Mirrors tests/test_regression/test_contest/test_add_problem.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_problem
@pytest.mark.regression
@pytest.mark.contest
def test_add_problem(contest_response_handler: ContestResponseHandler):
    """Add problem to contest."""
    contest_response_handler.post_add_problem()
