"""Mirrors tests/test_regression/test_recruit/test_post_team_invite.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.responses.recruit_response_handler import RecruitResponseHandler


@pytest.mark.regression
def test_post_team_invite(recruit_response_handler: RecruitResponseHandler):
    """Invite a team member to a company."""
    recruit_response_handler.post_create_invite(candidate_email=None, invite_type="team")
