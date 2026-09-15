"""Mirrors tests/test_regression/test_contest/test_add_only_theme_section.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.add_theme_section
@pytest.mark.regression
@pytest.mark.contest
def test_add_only_theme_section(contest_response_handler: ContestResponseHandler):
    """Add theme section in the contest landing page."""
    contest_response_handler.patch_add_theme_section()
