"""
Mirrors tests/test_regression/test_contest/test_update_contest_name.py (do-api-automation).
Source has no `@pytest.mark.contest` on this one — preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.update_contest_name
@pytest.mark.regression
def test_update_contest_name(contest_response_handler: ContestResponseHandler):
    """Update contest name."""
    contest_response_handler.patch_update_contest_name()
