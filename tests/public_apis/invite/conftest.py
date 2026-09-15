"""Mirrors tests/public_apis/invite/conftest.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_helpers import generate_future_date, generate_random_email
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.fixture(scope="function", autouse=True)
def create_invite(invite_response_handler: InviteResponseHandler):
    def _create_invite(slug):
        user_email = generate_random_email()
        payload = {
            "email": user_email,
            "expiry": generate_future_date(),
            "start_time": generate_future_date(1),
        }
        invite_response_handler.create_invite(slug, payload)
        return user_email

    return _create_invite
