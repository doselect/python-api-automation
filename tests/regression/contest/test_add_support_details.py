"""Mirrors tests/test_regression/test_contest/test_add_support_details.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.support_details
@pytest.mark.regression
@pytest.mark.contest
def test_support_details(contest_response_handler: ContestResponseHandler):
    """Add support details."""
    contest_response_handler.patch_add_support_details(True, action="both")
    contest_response_handler.patch_add_support_details(False, action="email")
    contest_response_handler.patch_add_support_details(False, action="phone")
