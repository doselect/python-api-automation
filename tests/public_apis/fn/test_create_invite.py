"""Mirrors tests/public_apis/fn/test_create_invite.py (do-api-automation)."""
from __future__ import annotations

import pytest

from src.core.do_api_config import FN_COMPANY_SLUG, FN_TEST_SLUG
from src.core.do_api_helpers import generate_future_date, generate_random_email, generate_random_string
from src.core.response_validator import validate_response_code
from src.responses.fn_response_handler import FnResponseHandler


@pytest.mark.public
@pytest.mark.naukri_campus
def test_fn_create_invite(fn_response_handler: FnResponseHandler, request):
    payload = {
        "fn_transcript_id": generate_random_string(),
        "fn_attempt_id": "sampleattempt2",
        "fn_job_id": "samplejob1",
        "fn_stage_id": "samplestage1",
        "fn_user_fullname": "user1",
        "fn_user_email": generate_random_email(),
        "fn_shard_id": "sampleshard1",
        "invite_settings": {
            "redirection_url": "https://www.firstnaukri.com",
            "web_proctoring": "False",
            "image_proctoring": "False",
            "image_proctoring_settings": {},
            "video_proctoring": "False",
            "video_proctoring_settings": {},
            "browser_tolerance": {"count": 10, "enabled": "False", "warning": "False"},
        },
        "test_slug": FN_TEST_SLUG,
        "customer_slug": FN_COMPANY_SLUG,
        "expiry": generate_future_date(),
        "suppress_email": True,
    }

    response = fn_response_handler.create_invite(payload)
    validate_response_code(request.node.name, response, 200)
    # Add more assertions based on expected response
