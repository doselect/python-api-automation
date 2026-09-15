"""
Mirrors tests/test_regression/test_contest/test_update_contest_type.py (do-api-automation). Source
has no `@pytest.mark.contest` on this one — preserved as-is. Source also uses
`@pytest.mark.update_contest_type`, which was missing from pyproject.toml's marker registry —
added there as part of this port (see DO_API_PORT_STATUS.md).
"""
from __future__ import annotations

import pytest

from src.responses.contest_response_handler import ContestResponseHandler


@pytest.mark.update_contest_type
@pytest.mark.regression
def test_update_contest_type(contest_response_handler: ContestResponseHandler):
    """Update contest type."""
    contest_response_handler.patch_update_contest_type(contest_type="hackathon")
    contest_response_handler.patch_update_contest_type(contest_type="coding_contest")
    contest_response_handler.patch_update_contest_type(contest_type="case_study")
    contest_response_handler.patch_update_contest_type(contest_type="hiring_challenge")
    contest_response_handler.patch_update_contest_type(contest_type="quiz")
