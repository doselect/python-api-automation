"""Mirrors tests/test_regression/test_contest/test_remove_only_prize_section.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.remove_prize_section
@pytest.mark.regression
@pytest.mark.contest
def test_remove_only_prize_section(contest_response_handler: ContestResponseHandler):
    """Remove the prize section from the contest landing page."""
    contest_response_handler.patch_remove_only_prize_section()
