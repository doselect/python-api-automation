"""
Mirrors tests/test_regression/test_contest/test_remove_two_section_theme_and_eligibility_section.py
(do-api-automation). Source has no `@pytest.mark.contest` on this one (unlike its siblings) —
preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.remove_two_section_theme_and_eligibility_section
@pytest.mark.regression
def test_remove_two_section_theme_and_eligibility_section(contest_response_handler: ContestResponseHandler):
    """Remove the theme and eligibilityCriteria sections from the contest landing page."""
    contest_response_handler.patch_remove_two_section_theme_and_eligibility_section()
