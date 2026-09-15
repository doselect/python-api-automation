"""
Mirrors tests/test_regression/test_contest/test_update_access_type.py (do-api-automation). Source
has no `@pytest.mark.contest` on this one — preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.update_contest_access_type
@pytest.mark.regression
def test_update_access_type(contest_response_handler: ContestResponseHandler):
    """Update contest access type."""
    contest_response_handler.patch_update_access_type(access_type="public")
    contest_response_handler.patch_update_access_type(access_type="invite_only")
