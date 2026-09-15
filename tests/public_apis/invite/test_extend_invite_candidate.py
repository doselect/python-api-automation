"""Mirrors tests/public_apis/invite/test_extend_invite_candidate.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL, TEST_SLUG_RECRUIT
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_extent_invite_candidate(invite_response_handler: InviteResponseHandler, request):
    candidate_email = CANDIDATE_EMAIL
    payload = {"minutes": 10}

    response = invite_response_handler.extend_invite_candidate(TEST_SLUG_RECRUIT, candidate_email, payload)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
