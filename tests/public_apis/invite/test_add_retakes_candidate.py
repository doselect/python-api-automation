"""Mirrors tests/public_apis/invite/test_add_retakes_candidate.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL, TEST_SLUG_LEARN
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_add_retakes_candidate(invite_response_handler: InviteResponseHandler, request):
    candidate_email = CANDIDATE_EMAIL
    payload = {"max_retakes": 1, "suppress_email": True, "expiry": "2030-05-29T15:17:35+05:30"}

    response = invite_response_handler.add_retakes_candidate(TEST_SLUG_LEARN, candidate_email, payload)
    validate_response_code(request.node.name, response, 201)
    # Add more assertions based on expected response
