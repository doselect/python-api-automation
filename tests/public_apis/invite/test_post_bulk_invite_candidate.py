"""Mirrors tests/public_apis/invite/test_post_bulk_invite_candidate.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import TEST_SLUG_RECRUIT
from src.core.do_api_helpers import generate_future_date, generate_random_email
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_post_bulk_invite_candidate(invite_response_handler: InviteResponseHandler, request):
    payload = {
        "objects": [
            {
                "email": generate_random_email(),
                "expiry": generate_future_date(),
                "suppress_email": True,
                "start_time": generate_future_date(1),
            },
            {
                "email": generate_random_email(),
                "expiry": generate_future_date(),
                "suppress_email": True,
                "start_time": generate_future_date(1),
            },
        ]
    }

    response = invite_response_handler.post_bulk_invite_candidate(TEST_SLUG_RECRUIT, payload)
    validate_response_code(request.node.name, response, 202)
    # Add more assertions based on expected response
