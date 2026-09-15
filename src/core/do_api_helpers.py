"""
Ports the generic (non-config, non-CSV) helpers from utils/generic_helpers.py in
https://github.com/doselect/do-api-automation.git that ported tests actually call. Extended
on-demand as later domains need more of that file (see DO_API_PORT_STATUS.md) — this is not the
whole source file.
"""
from __future__ import annotations

import random
import re
import string
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import allure
import requests
from faker import Faker

from src.core.do_api_logger import setup_logger

faker = Faker()


def generate_random_email() -> str:
    """Mirrors utils.generic_helpers.generate_random_email()."""
    name = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{name}@yopmail.com"


def generate_random_string(length: int = 10) -> str:
    """Mirrors utils.generic_helpers.generate_random_string(length)."""
    prefix = "transcript"
    random_suffix = "".join(random.choices(string.ascii_letters + string.digits, k=length))
    return prefix + random_suffix


def generate_future_date(days_ahead: int = 10) -> str:
    """Mirrors utils.generic_helpers.generate_future_date(days_ahead)."""
    ist_offset = timedelta(hours=5, minutes=30)
    ist_timezone = timezone(ist_offset)
    future_date = datetime.now(ist_timezone) + timedelta(days=days_ahead)
    return future_date.strftime("%Y-%m-%dT%H:%M:%S%z")


def get_current_ist_datetime() -> str:
    """Mirrors utils.generic_helpers.get_current_ist_datetime()."""
    ist_offset = timedelta(hours=5, minutes=30)
    ist_timezone = timezone(ist_offset)
    current_time = datetime.now(ist_timezone) + timedelta(seconds=5)
    return current_time.strftime("%Y-%m-%dT%H:%M:%S%z")


def generate_fake_name() -> str:
    """Mirrors utils.generic_helpers.generate_fake_name()."""
    return faker.name()


def attach_details_to_allure(request, response, name: str) -> None:
    """
    Mirrors utils.generic_helpers.attach_details_to_allure(request, response, name): used by the
    regression_api_methods/* step functions (doiq, recruit, interview, ...), which build their
    own raw `requests` call instead of going through rest_client.execute_request (that already
    does its own Allure attach) — so this is ported separately for those call sites.
    """
    allure.attach(
        f"Request details: {request}",
        name=name + " Request",
        attachment_type=allure.attachment_type.TEXT,
    )
    allure.attach(
        f"Response Status: {response.status_code}\nResponse Headers: {dict(response.headers)}\n"
        f"Response Content: {response.text[:1000] if response.text else 'No content'}",
        name=name + " Response",
        attachment_type=allure.attachment_type.TEXT,
    )


def get_sid_from_response(response: str) -> Optional[str]:
    """
    Mirrors utils.generic_helpers.get_sid_from_response(response): pulls Socket.IO's `sid` out of
    a long-polling handshake body (a `"sid":"<value>"` substring), used by the hacker domain's
    connect_websocket to thread the polling `sid` into the follow-up POST/GET calls and the
    handshake `sock_id` used by post_code_run's sockmeta. Same regex as the source, byte-for-byte.
    """
    match_sid = re.search(r'"sid":"(.*?)"', response)
    return match_sid.group(1) if match_sid else None


def encode_url(value: str) -> str:
    """Mirrors utils.generic_helpers.encode_url(value): safe-quotes a value for a query string."""
    return urllib.parse.quote(value, safe="")


def decode_url(value: str) -> str:
    """Mirrors utils.generic_helpers.decode_url(value): decode a URL-encoded string."""
    return urllib.parse.unquote(value)


def document_keys(data: Any, current_path: str = "") -> list[str]:
    """
    Mirrors utils.generic_helpers.document_keys(data, current_path): a debugging aid the
    `content_creator`/`recruit` regression_api_methods import but never actually use the return
    value of (every call site assigns it to an unused local) — ported for completeness only, no
    call site in this framework needs to call it.

    Preserves a source quirk verbatim: the recursive `document_keys(value, new_path)` call's
    return value is discarded rather than merged in, so only the *immediate* children's paths are
    ever collected, not the full nested tree the recursion visits. Left as-is rather than "fixed",
    since the function is unused dead code either way.
    """
    key_paths: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = f"{current_path}.{key}" if current_path else key
            key_paths.append(new_path)
            document_keys(value, new_path)
    elif isinstance(data, list) and data:
        new_path = f"{current_path}[i]"
        key_paths.append(new_path)
        document_keys(data[0], new_path)
    return key_paths


def retry_api_call(
    url: str,
    headers: dict,
    params: Optional[dict[str, Any]],
    method: str = "get",
    max_retries: int = 4,
    retry: int = 1,
) -> requests.Response:
    """
    Mirrors utils.generic_helpers.retry_api_call(url, headers, params, method, max_retries, retry):
    sleeps `10 * (max_retries - retry)` seconds (a linearly-shrinking backoff) then re-issues the
    request once, unasserted — used by the `recruit` domain's get_solution.py/get_test_candidates.py
    retry loops. Byte-for-byte port, including the always-`10*(max_retries-retry)` sleep (0 on the
    final retry, same as the source).
    """
    time.sleep(10 * (max_retries - retry))
    logger = setup_logger(__name__)
    logger.info(f"Retrying... {retry} times")
    return requests.request(method=method, url=url, headers=headers, params=params)
