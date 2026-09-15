"""Mirrors tests/test_regression/test_contest/test_make_prize_and_eligibility_section_private.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.make_section_private
@pytest.mark.regression
@pytest.mark.contest
def test_make_section_private(contest_response_handler: ContestResponseHandler):
    """Update to make sections private."""
    contest_response_handler.patch_make_section_private()
