"""
Mirrors tests/test_regression/test_contest/test_section_name_visibility.py (do-api-automation).
Source has no `@pytest.mark.contest` on this one — preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.section_name_visibility
@pytest.mark.regression
def test_section_name_visibility(contest_response_handler: ContestResponseHandler):
    """Section name visibility to candidate."""
    contest_response_handler.patch_section_name_visibility(True)
    contest_response_handler.patch_section_name_visibility(False)
