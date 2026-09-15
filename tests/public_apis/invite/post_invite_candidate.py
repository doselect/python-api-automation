"""
Mirrors tests/public_apis/invite/post_invite_candidate.py (do-api-automation): a reusable
step function (not a pytest test — no `test_` prefix, no marker) imported directly by the
hacker-domain attempt flows (test_attempt_coding.py, test_attempt_dba.py, test_attempt_fib.py,
test_attempt_mcq.py, test_attempt_subjective.py — see DO_API_PORT_STATUS.md, hacker domain
pending). Builds its own spec builder/response handler rather than taking them as pytest
fixtures, since it's called as a plain function from within another test, not collected itself.
"""
from __future__ import annotations

from src.core.do_api_config import TEST_SLUG_RECRUIT
from src.core.do_api_helpers import generate_random_email
from src.core.response_validator import validate_response_code
from src.responses.invite_response_handler import InviteResponseHandler
from src.specs.invite_spec_builder import InviteSpecBuilder


def post_invite_candidate(request, shared_data: dict, test_slug: str = TEST_SLUG_RECRUIT) -> dict:
    spec_builder = InviteSpecBuilder()
    spec_builder.setup_all_specs()
    response_handler = InviteResponseHandler(spec_builder)

    email = generate_random_email()
    payload = {
        "email": email,
        # "expiry": generate_future_date(),
        # "start_time": get_current_ist_datetime(),
    }
    shared_data["invited_email"] = email

    response, access_code = response_handler.post_invite_candidate_and_get_access_code(test_slug, payload)
    shared_data["access_code"] = access_code
    validate_response_code(request.node.name, response, 201)
    return {
        "status_code": response.status_code,
        "access_code": access_code,
        "email": email,
    }
