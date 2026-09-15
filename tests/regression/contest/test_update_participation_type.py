"""
Mirrors tests/test_regression/test_contest/test_update_participation_type.py (do-api-automation).
Source has no `@pytest.mark.contest` on this one — preserved as-is.
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.update_contest_participation_type
@pytest.mark.regression
def test_update_participation_type(contest_response_handler: ContestResponseHandler):
    """Test PATCH update to change contest participation type."""
    contest_response_handler.patch_update_participation_type(
        participation_type="team", min_team_size=1, max_team_size=2
    )
    contest_response_handler.patch_update_participation_type(
        participation_type="individual", min_team_size=0, max_team_size=0
    )
