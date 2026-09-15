"""Mirrors tests/public_apis/invite/test_delete_invite_candidate.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import TEST_SLUG_RECRUIT
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_delete_invite_candidate(create_invite, invite_response_handler: InviteResponseHandler, request):
    user_email = create_invite(TEST_SLUG_RECRUIT)

    response = invite_response_handler.delete_invite_candidate(TEST_SLUG_RECRUIT, user_email)
    validate_response_code(request.node.name, response, 204)
    # Add more assertions based on expected response
