"""
Ports tests/regression_api_methods/interview/get_email_otp.py::get_otp_from_email_helper from
https://github.com/doselect/do-api-automation.git — a real IMAP read (via `src.core.email_reader`),
not an HTTP call. `shared_data` threading is dropped (this framework threads data via explicit
return values instead); the returned dict is unchanged otherwise, so callers get the same
{"status_code", "otp", "subject", "attempts", "message"} shape the source stashed piecemeal into
shared_data.
"""
from __future__ import annotations

import time
from typing import Optional

from src.core.do_api_config import AUTOMATION_EMAIL
from src.core.do_api_helpers import attach_details_to_allure
from src.core.do_api_logger import setup_logger
from src.core.email_reader import get_otp_from_email

logger = setup_logger(__name__)


def get_otp_from_email_helper(
    subject_to_search: str,
    imap_server: str = "imap.gmail.com",
    max_retries: int = 3,
    delay_seconds: int = 10,
) -> dict:
    """
    Mirrors get_email_otp.py::get_otp_from_email_helper(subject_to_search, imap_server,
    shared_data, max_retries, delay_seconds) — returns the same result dict the source built,
    minus the `shared_data` side-channel writes (source stashed the same fields into
    shared_data["email_otp"/"email_otp_error"/"email_otp_attempts"]).
    """
    otp: Optional[str] = None
    attempts = 0
    error_message: Optional[str] = None

    try:
        logger.info(f"Using email: {AUTOMATION_EMAIL}")
        for attempt in range(max_retries):
            attempts = attempt + 1
            logger.info(f"Attempt {attempts}/{max_retries} to get OTP")
            otp = get_otp_from_email(subject_to_search, imap_server)
            logger.info(f"OTP: {otp}")

            if otp:
                logger.info(f"Successfully extracted OTP: {otp}")
                return {
                    "status_code": 200,
                    "otp": otp,
                    "subject": subject_to_search,
                    "attempts": attempts,
                    "message": f"OTP extracted successfully: {otp}",
                }

            if attempt < max_retries - 1:
                logger.info(f"OTP not found, waiting {delay_seconds} seconds before retry")
                time.sleep(delay_seconds)

        error_message = f"No OTP found in emails with subject: {subject_to_search} after {max_retries} attempts"
        logger.warning(error_message)
        return {
            "status_code": 404,
            "otp": None,
            "subject": subject_to_search,
            "attempts": max_retries,
            "message": error_message,
        }

    except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
        error_message = f"Error getting OTP from email: {e}"
        logger.error(error_message)
        return {
            "status_code": 500,
            "otp": None,
            "subject": subject_to_search,
            "attempts": attempts,
            "message": error_message,
        }
    finally:
        mock_response = type(
            "MockResponse",
            (),
            {
                "status_code": 200 if otp else (404 if attempts == max_retries else 500),
                "text": f"OTP: {otp}, Attempts: {attempts}, Error: {error_message}",
                "headers": {},
            },
        )()

        attach_details_to_allure(
            request={
                "email": AUTOMATION_EMAIL,
                "subject": subject_to_search,
                "imap_server": imap_server,
                "max_retries": max_retries,
                "delay_seconds": delay_seconds,
            },
            response=mock_response,
            name="Get OTP from Email",
        )
