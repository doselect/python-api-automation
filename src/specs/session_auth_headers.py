"""
Ports the `generate_headers`/`get_default_headers` dispatcher from utils/header_generator.py
(https://github.com/doselect/do-api-automation.git) for the `"default"` api_identifier case —
i.e. `generate_headers(user_type, "default", shared_data)`. The many `api_identifier`-specific
branches (get_test_details, get_solution, ...) are ported directly into each domain's own
spec builder instead of through this dispatcher, matching how this framework already
centralizes one spec builder per domain.

`shared_data["<role>_csrf_token"]`/`["<role>_cookie"]` become `auth_manager.csrf_token`/
`auth_manager.cookie` here — the session-auth domains build an AuthManager per test (see
tests/regression/doiq/conftest.py) instead of stuffing tokens into a shared dict.
"""
from __future__ import annotations

from typing import Optional

from src.core.auth_manager import AuthManager
from src.core.do_api_config import DO_TEST_INTERFACE_DOMAIN, DOSELECT_PRIMARY_DOMAIN


def default_recruiter_headers(auth_manager: AuthManager, only_auth: bool = False) -> dict[str, str]:
    """Mirrors get_default_headers("recruiter", shared_data, only_auth)."""
    if only_auth:
        return {"x-csrftoken": auth_manager.csrf_token, "Cookie": auth_manager.cookie}
    return {
        "accept": "application/json, text/plain, */*",
        "x-csrftoken": auth_manager.csrf_token,
        "Cookie": auth_manager.cookie,
        "referer": f"{DOSELECT_PRIMARY_DOMAIN}/recruit",
    }


def default_hacker_headers(auth_manager: AuthManager, only_auth: bool = False) -> dict[str, str]:
    """Mirrors get_default_headers("hacker", shared_data, only_auth)."""
    if only_auth:
        return {"x-csrftoken": auth_manager.csrf_token, "Cookie": auth_manager.cookie}
    return {
        "accept": "application/json, text/plain, */*",
        "x-csrftoken": auth_manager.csrf_token,
        "Cookie": auth_manager.cookie,
        "origin": DO_TEST_INTERFACE_DOMAIN,
        "referer": DO_TEST_INTERFACE_DOMAIN,
    }


def default_content_creator_headers(auth_manager: AuthManager, only_auth: bool = False) -> dict[str, str]:
    """Mirrors get_default_headers("content_creator", shared_data, only_auth)."""
    if only_auth:
        return {"x-csrftoken": auth_manager.csrf_token, "Cookie": auth_manager.cookie}
    return {
        "accept": "application/json, text/plain, */*",
        "x-csrftoken": auth_manager.csrf_token,
        "Cookie": auth_manager.cookie,
        "referer": f"{DOSELECT_PRIMARY_DOMAIN}/creator/problems",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "content-type": "application/json;charset=UTF-8",
        "origin": DOSELECT_PRIMARY_DOMAIN,
    }


def default_reviewer_headers(auth_manager: AuthManager, only_auth: bool = False) -> dict[str, str]:
    """Mirrors get_default_headers("reviewer", shared_data, only_auth)."""
    if only_auth:
        return {"x-csrftoken": auth_manager.csrf_token, "Cookie": auth_manager.cookie}
    return {
        "accept": "application/json, text/plain, */*",
        "x-csrftoken": auth_manager.csrf_token,
        "Cookie": auth_manager.cookie,
        "referer": f"{DOSELECT_PRIMARY_DOMAIN}/creator/problems",
        "accept-language": "en-US,en;q=0.9",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "content-type": "application/json;charset=UTF-8",
        "origin": DOSELECT_PRIMARY_DOMAIN,
    }
