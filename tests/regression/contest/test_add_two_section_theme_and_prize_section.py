"""Mirrors tests/test_regression/test_contest/test_add_two_section_theme_and_prize_section.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_two_section_theme_and_prize_section
@pytest.mark.regression
@pytest.mark.contest
def test_add_two_section_theme_and_prize_section(contest_response_handler: ContestResponseHandler):
    """Add theme and prize sections in the contest landing page."""
    contest_response_handler.patch_add_two_section_theme_and_prize_section()
