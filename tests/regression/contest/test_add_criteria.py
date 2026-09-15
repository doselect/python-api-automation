"""Mirrors tests/test_regression/test_contest/test_add_criteria.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_criteria
@pytest.mark.regression
@pytest.mark.contest
def test_add_criteria(contest_response_handler: ContestResponseHandler):
    """Updating contest criteria."""
    contest_response_handler.patch_add_criteria()
