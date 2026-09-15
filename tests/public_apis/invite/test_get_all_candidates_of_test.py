"""Mirrors tests/public_apis/invite/test_get_all_candidates_of_test.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import TEST_SLUG_RECRUIT
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler


@pytest.mark.public
def test_get_all_candidates_of_test(invite_response_handler: InviteResponseHandler, request):
    response = invite_response_handler.get_all_candidates_of_test(TEST_SLUG_RECRUIT)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
