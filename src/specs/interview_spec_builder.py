"""
Ports the header-building side of tests/regression_api_methods/interview/*.py
(do-api-automation). Investigated per-file (not assumed) how each endpoint authenticates:

  - Every interview-management call (job roles, interviews, feedback, scheduling, ...) calls
    `generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` with NO further `.update()`
    override at any call site — i.e. interview management is done as the recruiter role, using
    the exact same header set `default_recruiter_headers` already ports. That covers every
    endpoint below except the two genuinely distinct cases:
  - `get_interview_gateway.py` merges TWO header sets: the literal, unrelated-to-auth
    `get_interview_gateway_headers(shared_data)` dict (an unauthenticated page-navigation-style
    GET's browser headers) overlaid with `generate_headers(USER_TYPE_RECRUITER, "default", ...)`
    (whose cookie/csrf/referer/accept win over the literal dict's matching keys). Ported as
    `interview_gateway_spec`.
  - `post_send_otp.py` calls `generate_headers(USER_TYPE_INTERVIEWER, "default", shared_data)`.
    `utils.config.USER_TYPE_INTERVIEWER = "interviewer"`, but `get_default_headers`'s
    `match user_type` has cases only for "recruiter"/"hacker"/"content_creator"/"reviewer" — no
    "interviewer" case — so for this one call `base_headers` never gets any cookie/csrf added and
    the function returns just `{"accept": "application/json, text/plain, */*"}`. This is a
    genuinely unauthenticated call (OTP send to a candidate over a public interview link), ported
    as `send_otp_spec` with that literal header (no AuthManager involvement at all).
"""
from __future__ import annotations

from typing import Optional

from src.constants.paths import interview_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.specs.session_auth_headers import default_recruiter_headers

# Mirrors utils.header_generator.get_interview_gateway_headers(shared_data) — a literal dict,
# unrelated to any user_type/auth dispatch (the function ignores its `shared_data` argument).
INTERVIEW_GATEWAY_HEADERS: dict[str, str] = {
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,"
        "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
    ),
    "accept-language": "en-IN,en;q=0.9",
    "dnt": "1",
    "priority": "u=0, i",
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
}


class InterviewSpecBuilder:
    """Builds the reusable request specs for the ported `interview` regression endpoints."""

    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager

    def default_spec(self, path: str, base_url: Optional[str] = None) -> RequestSpec:
        """
        Mirrors `generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` — the header set
        used by every interview-management endpoint (job roles, interviews, feedback, scheduling,
        problem search, ...). `base_url` defaults to `DOSELECT_PRIMARY_DOMAIN`; pass
        `interview_api_path.dolores_base_url()` for `get_active_interviewers.py`'s
        `/search/interviewers` call (same header set, different host).
        """
        return build_request_spec(
            base_url=base_url or interview_api_path.set_base_url(), base_path=path,
            headers=default_recruiter_headers(self._auth_manager),
        )

    def interview_gateway_spec(self, gateway_token: str) -> RequestSpec:
        """
        Mirrors get_interview_gateway.py's header merge: `INTERVIEW_GATEWAY_HEADERS` overlaid with
        `default_recruiter_headers` (matching keys — accept/x-csrftoken/Cookie/referer — win, the
        rest of the literal browser-fingerprint dict passes through unchanged).
        """
        headers = dict(INTERVIEW_GATEWAY_HEADERS)
        headers.update(default_recruiter_headers(self._auth_manager))
        return build_request_spec(
            base_url=interview_api_path.gateway_base_url(), base_path=interview_api_path.GATEWAY,
            headers=headers, path_params={"gatewayToken": gateway_token},
        )

    def send_otp_spec(self) -> RequestSpec:
        """
        Mirrors post_send_otp.py's `generate_headers(USER_TYPE_INTERVIEWER, "default", shared_data)`
        — see module docstring: `get_default_headers` has no "interviewer" case, so only the
        unauthenticated base header is ever returned. No AuthManager access here at all.
        """
        return build_request_spec(
            base_url=interview_api_path.set_base_url(), base_path=interview_api_path.SEND_OTP,
            headers={"accept": "application/json, text/plain, */*"},
        )
