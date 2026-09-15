"""
Ports the header-building side of tests/regression_api_methods/hacker/*.py
(https://github.com/doselect/do-api-automation.git).

Unlike every other session-auth domain ported so far (recruit/interview/doiq/ai_interview/
content_creator), the hacker/candidate side never calls `POST /login` via AuthManager — the source
never builds a hacker `AuthManager` either. Instead `shared_data["hacker_csrf_token"]`/
`["hacker_cookie"]` are populated by hand from response cookies returned by GET/POST
`/gateways/test` (see get_test_gateway.py / post_test_gateway_submit.py — the "test invite link"
flow: a recruiter-issued `access_code` is exchanged for a session, never a username/password
login). `CandidateSession` below is a small mutable stand-in that duck-types AuthManager's
`csrf_token`/`cookie` attributes (the only two `default_hacker_headers` touches) so that function
can still be reused as-is; HackerSpecBuilder rebuilds headers from it lazily on every call, exactly
like DoiqSpecBuilder does with a real AuthManager, since the token/cookie mutate mid-flow (first
set by get_test_gateway, then replaced by post_test_gateway_submit).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.constants.paths import hacker_api_path
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.core.do_api_helpers import encode_url
from src.specs.session_auth_headers import default_hacker_headers


@dataclass
class CandidateSession:
    """
    Mutable stand-in for the candidate's `shared_data["hacker_csrf_token"]`/`["hacker_cookie"]`.
    Starts empty; get_test_gateway/post_test_gateway_submit populate it as the real flow runs.
    """

    csrf_token: str = ""
    cookie: str = ""


class HackerSpecBuilder:
    """Builds the reusable request specs for the ported `hacker` regression endpoints."""

    def __init__(self, session: CandidateSession) -> None:
        self._session = session

    # -- gateways/test (unauthenticated GET, then two authenticated form POSTs) -----------------

    def test_gateway_get_spec(self) -> RequestSpec:
        """Mirrors get_test_gateway.py — no headers at all (the source never passes any)."""
        return build_request_spec(
            base_url=hacker_api_path.set_base_url(), base_path=hacker_api_path.TEST_GATEWAY, headers={}
        )

    def test_gateway_post_spec(self, access_code: str) -> RequestSpec:
        """Mirrors post_test_gateway.py's headers (default + origin/referer override with the access code)."""
        encoded_access_code = encode_url(access_code)
        headers = default_hacker_headers(self._session)
        headers.update(
            {
                "origin": hacker_api_path.set_base_url(),
                "referer": f"{hacker_api_path.set_base_url()}/gateways/test?access_code={encoded_access_code}",
            }
        )
        return build_request_spec(
            base_url=hacker_api_path.set_base_url(), base_path=hacker_api_path.TEST_GATEWAY, headers=headers
        )

    def test_gateway_submit_spec(self) -> RequestSpec:
        """Mirrors post_test_gateway_submit.py's headers (plain default hacker headers, no overrides)."""
        return build_request_spec(
            base_url=hacker_api_path.set_base_url(), base_path=hacker_api_path.TEST_GATEWAY,
            headers=default_hacker_headers(self._session),
        )

    # -- everything else: plain default hacker headers, no overrides -----------------------------

    def _default_spec(self, base_path: str) -> RequestSpec:
        return build_request_spec(
            base_url=hacker_api_path.set_base_url(), base_path=base_path, headers=default_hacker_headers(self._session)
        )

    def server_time_spec(self) -> RequestSpec:
        """Mirrors get_server_time.py."""
        return self._default_spec(hacker_api_path.SERVER_TIME)

    def technologies_spec(self) -> RequestSpec:
        """Mirrors get_technologies.py."""
        return self._default_spec(hacker_api_path.TECHNOLOGIES)

    def identity_gateway_spec(self) -> RequestSpec:
        """Mirrors get_identity_gateway.py."""
        return self._default_spec(hacker_api_path.IDENTITY_GATEWAY)

    def hacker_details_spec(self) -> RequestSpec:
        """Mirrors get_hacker_details.py."""
        return self._default_spec(hacker_api_path.HACKER_DETAIL)

    def infra_allocate_spec(self) -> RequestSpec:
        """Mirrors get_infra_allocate.py."""
        return self._default_spec(hacker_api_path.INFRA_ALLOCATE)

    def sectionwise_problems_spec(self) -> RequestSpec:
        """Mirrors get_sectionwise_problems.py."""
        return self._default_spec(hacker_api_path.SECTIONWISE_PROBLEMS)

    def assessment_problems_spec(self) -> RequestSpec:
        """Mirrors get_assessment_problems.py."""
        return self._default_spec(hacker_api_path.ASSESSMENT_PROBLEMS)

    def solution_list_spec(self) -> RequestSpec:
        """Mirrors post_create_solution.py."""
        return self._default_spec(hacker_api_path.SOLUTION_LIST)

    def solution_detail_spec(self) -> RequestSpec:
        """Mirrors patch_solution.py."""
        return self._default_spec(hacker_api_path.SOLUTION_DETAIL)

    def code_run_spec(self) -> RequestSpec:
        """Mirrors post_code_run.py."""
        return self._default_spec(hacker_api_path.CODE_RUN)

    def test_init_spec(self) -> RequestSpec:
        """Mirrors post_test_init.py."""
        return self._default_spec(hacker_api_path.TEST_INIT)

    def test_start_spec(self) -> RequestSpec:
        """Mirrors post_test_start.py."""
        return self._default_spec(hacker_api_path.TEST_START)

    def test_submit_all_spec(self) -> RequestSpec:
        """Mirrors post_test_submit_all.py."""
        return self._default_spec(hacker_api_path.TEST_SUBMIT_ALL)

    def solutions_submit_spec(self) -> RequestSpec:
        """Mirrors tests/regression_api_methods/recruit/post_submit_solution.py (candidate-authed, hence ported here)."""
        return self._default_spec(hacker_api_path.SOLUTIONS_SUBMIT)

    def test_details_spec(self) -> RequestSpec:
        """Mirrors get_test_details.py's "hacker" branch (default + `accept-language` addition)."""
        headers = default_hacker_headers(self._session)
        headers["accept-language"] = "en-US,en;q=0.9"
        return build_request_spec(
            base_url=hacker_api_path.set_base_url(), base_path=hacker_api_path.TEST_DETAIL, headers=headers
        )

    # -- Socket.IO long-polling handshake (WEBSOCKET_DOMAIN base) --------------------------------

    def websocket_polling_spec(self) -> RequestSpec:
        """Mirrors get_websocket_polling_one/two.py and post_websocket_polling.py's headers/base URL."""
        return build_request_spec(
            base_url=hacker_api_path.set_websocket_base_url(), base_path=hacker_api_path.SOCKET_IO,
            headers=default_hacker_headers(self._session),
        )
