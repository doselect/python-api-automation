"""Mirrors tests/public_apis/invite/test_update_invite_candidate.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import TEST_SLUG_RECRUIT
from src.core.do_api_helpers import generate_future_date
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_update_invite_candidate(create_invite, invite_response_handler: InviteResponseHandler, request):
    candidate_email = create_invite(TEST_SLUG_RECRUIT)
    payload = {"expiry": generate_future_date(), "start_time": generate_future_date(1)}

    response = invite_response_handler.update_invite_candidate(TEST_SLUG_RECRUIT, candidate_email, payload)
    validate_response_code(request.node.name, response, 202)
    # Add more assertions based on expected response
