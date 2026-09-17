"""
Mirrors tests/test_regression/test_interview/test_email_otp_reading.py (do-api-automation), but
primes its own OTP email via `post_send_otp` first instead of assuming one is already sitting in
the shared mailbox. The source only passed because it ran, in a fixed suite order, right after
another test had triggered an OTP send and nothing had consumed it since — under this framework's
per-test fixtures (and especially under parallel workers, see [[parallel-worker-races]]) that's not
guaranteed, so this primes its own state the same way test_get_doiq_converstation.py does, deviating
from the source rather than being order-dependently flaky. Source doesn't assert anything (it only
logs the result dict), which means it would report PASS even with no email credentials configured
(the helper swallows every exception and always returns a result dict) — an `assert` is added here
so this test fails meaningfully (AssertionError, not ImportError/TypeError) when
AUTOMATION_EMAIL/AUTOMATION_PASSWORD/IMAP connectivity aren't available, matching every other
ported test's "fails only on missing live creds/connectivity" behavior.
"""
from __future__ import annotations

import time

import pytest

from src.core.do_api_config import CANDIDATE_EMAIL_INTERVIEW
from src.core.do_api_helpers import generate_fake_name
from src.helpers.interview.email_otp import get_otp_from_email_helper
from src.responses.interview_response_handler import InterviewResponseHandler


@pytest.mark.regression
def test_email_otp_reading_workflow(interview_response_handler: InterviewResponseHandler):
    session_interview_token = interview_response_handler.get_or_create_fresh_token()
    interview_slug = interview_response_handler.get_interview_meta(session_interview_token)
    interview_response_handler.post_send_otp(
        full_name=generate_fake_name(), email=CANDIDATE_EMAIL_INTERVIEW,
        interview_slug=interview_slug, interview_token=session_interview_token,
    )
    time.sleep(15)

    result = get_otp_from_email_helper(
        subject_to_search="DoSelect Email Verification", max_retries=3, delay_seconds=10,
    )
    assert result["otp"], f"Failed to read OTP from email: {result}"
