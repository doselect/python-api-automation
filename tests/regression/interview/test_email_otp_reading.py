"""
Mirrors tests/test_regression/test_interview/test_email_otp_reading.py (do-api-automation). Real
IMAP call (see src/core/email_reader.py) — no session-auth fixture needed, so this doesn't use
`interview_response_handler`. Source doesn't assert anything (it only logs the result dict), which
means it would report PASS even with no email credentials configured (the helper swallows every
exception and always returns a result dict) — an `assert` is added here so this test fails
meaningfully (AssertionError, not ImportError/TypeError) when AUTOMATION_EMAIL/AUTOMATION_PASSWORD/
IMAP connectivity aren't available, matching every other ported test's "fails only on missing live
creds/connectivity" behavior.
"""
from __future__ import annotations

import pytest

from src.helpers.interview.email_otp import get_otp_from_email_helper


@pytest.mark.regression
def test_email_otp_reading_workflow():
    result = get_otp_from_email_helper(
        subject_to_search="DoSelect Email Verification", max_retries=3, delay_seconds=10,
    )
    assert result["otp"], f"Failed to read OTP from email: {result}"
