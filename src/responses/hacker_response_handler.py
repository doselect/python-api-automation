"""
Ports tests/regression_api_methods/hacker/*.py (do-api-automation): one method per source
function, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (same rationale as doiq_response_handler.py's docstring — same
requests, same status assertions, same payloads).

`post_submit_solution` (tests/regression_api_methods/recruit/post_submit_solution.py in the
source) is ported here rather than under `recruit` — it authenticates via
`generate_headers(USER_TYPE_CANDIDATE, "default", shared_data)` and its payload lives in
payloads/regression/hacker/solutions_submit.py, so it is functionally a hacker/candidate endpoint
despite the source folder it sits in.

`connect_websocket`'s three-call sequence (get_websocket_polling_one -> post_websocket_polling ->
get_websocket_polling_two) + the by-hand cookie merge + `get_sid_from_response` extraction are
collapsed into one `connect_websocket` method here, same as the source.

Three calls bypass execute_request and go straight to `requests` (documented deviation, same
rationale as ai_interview_response_handler.py::post_upload_file): post_test_gateway/
post_test_gateway_submit POST HTML form data (`data=<dict>`), not a JSON body, and
post_test_gateway_submit also needs `response.history[0].cookies` (the redirect hop) which
execute_request's single `requests.request(...)` call doesn't expose; post_websocket_polling posts
a raw string body ("40", a Socket.IO CONNECT packet), also not JSON.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any, Optional

import requests

from src.core.do_api_config import RECRUITER_USERNAME
from src.core.do_api_helpers import encode_url, generate_fake_name, get_sid_from_response
from src.core.rest_client import execute_get_request_without_status_assertion, execute_request
from src.helpers.hacker.payloads import (
    code_run_payload,
    get_patch_payload,
    get_solution_payload,
    get_submit_solution_payload,
)
from src.specs.hacker_spec_builder import CandidateSession, HackerSpecBuilder


def _merge_cookie(existing_cookie: str, response: requests.Response) -> str:
    """Mirrors get_websocket_polling_one.py's by-hand cookie merge (new cookies take precedence)."""
    existing: dict[str, str] = {}
    if existing_cookie:
        for cookie in existing_cookie.split("; "):
            if "=" in cookie:
                name, value = cookie.split("=", 1)
                existing[name] = value
    merged = {**existing, **requests.utils.dict_from_cookiejar(response.cookies)}
    return "; ".join(f"{name}={value}" for name, value in merged.items())


class HackerResponseHandler:
    """Wraps a HackerSpecBuilder to centralize the ported `hacker` regression API calls."""

    def __init__(self, spec_builder: HackerSpecBuilder, session: CandidateSession) -> None:
        self._spec_builder = spec_builder
        self._session = session

    # -- gateways/test: access_code -> candidate session (the "test invite link" flow) -----------

    def get_test_gateway(self, access_code: str) -> dict[str, Any]:
        """Mirrors get_test_gateway.py: unauthenticated GET, seeds the candidate session from cookies."""
        encoded_access_code = encode_url(access_code)
        response = execute_request(
            self._spec_builder.test_gateway_get_spec(), "GET", query_params={"access_code": encoded_access_code},
            expected_status_code=200,
        )
        cookie_dict = requests.utils.dict_from_cookiejar(response.cookies)
        self._session.csrf_token = cookie_dict.get("doselectcsrf")
        self._session.cookie = "; ".join(f"{k}={v}" for k, v in cookie_dict.items())
        return {"status_code": response.status_code}

    def post_test_gateway(self, access_code: str) -> dict[str, Any]:
        """Mirrors post_test_gateway.py: form POST, does not touch the candidate session's cookie."""
        encoded_access_code = encode_url(access_code)
        spec = self._spec_builder.test_gateway_post_spec(access_code)
        data = {
            "csrfmiddlewaretoken": self._session.csrf_token,
            "access_code": encoded_access_code,
            "test_type": "None",
        }
        response = requests.post(
            url=spec.base_url.rstrip("/") + spec.base_path, headers=spec.headers, data=data,
            timeout=spec.timeout_ms / 1000,
        )
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200, got {response.status_code}")
        return {"status_code": response.status_code}

    def post_test_gateway_submit(self, access_code: str) -> dict[str, Any]:
        """Mirrors post_test_gateway_submit.py: form POST, replaces the candidate session's csrf/cookie."""
        encoded_access_code = encode_url(access_code)
        spec = self._spec_builder.test_gateway_submit_spec()
        data = {
            "csrfmiddlewaretoken": self._session.csrf_token,
            "full_name": generate_fake_name(),
            "access_code": encoded_access_code,
        }
        response = requests.post(
            url=spec.base_url.rstrip("/") + spec.base_path, headers=spec.headers, data=data,
            allow_redirects=True, timeout=spec.timeout_ms / 1000,
        )
        cookie_dict = requests.utils.dict_from_cookiejar(response.history[0].cookies)
        self._session.csrf_token = cookie_dict.get("doselectcsrf")
        self._session.cookie = "; ".join(f"{k}={v}" for k, v in cookie_dict.items())
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200, got {response.status_code}")
        return {"status_code": response.status_code}

    # -- plain reads/writes -------------------------------------------------------------------

    def get_server_time(self, expected_status_code: int = 200) -> dict[str, Any]:
        """Mirrors get_server_time.py."""
        response = execute_request(
            self._spec_builder.server_time_spec(), "GET", expected_status_code=expected_status_code
        )
        return {"status_code": response.status_code}

    def get_technologies(self, expected_status_code: int = 200) -> dict[str, Any]:
        """Mirrors get_technologies.py."""
        response = execute_request(
            self._spec_builder.technologies_spec(), "GET", expected_status_code=expected_status_code
        )
        return {"status_code": response.status_code}

    def get_identity_gateway(self, expected_status_code: int = 200) -> dict[str, Any]:
        """Mirrors get_identity_gateway.py."""
        response = execute_request(
            self._spec_builder.identity_gateway_spec(), "GET", expected_status_code=expected_status_code
        )
        data = response.json()
        return {"status_code": response.status_code, "candidate_username": data["username"], "user_role_id": data["user_role_id"]}

    def get_hacker_details(
        self, user_role_id: str, candidate_username: str, expected_status_code: int = 200
    ) -> dict[str, Any]:
        """Mirrors get_hacker_details.py."""
        params = {"__env": "PLT", "__user": candidate_username}
        response = execute_request(
            self._spec_builder.hacker_details_spec(), "GET", path_params={"hackerId": user_role_id},
            query_params=params, expected_status_code=expected_status_code,
        )
        return {"status_code": response.status_code}

    def get_test_details(
        self, test_slug: str, candidate_username: str, expected_status_code: int = 200
    ) -> dict[str, Any]:
        """Mirrors tests/regression_api_methods/common/get_test_details.py's "hacker" branch."""
        params = {"is_test_env": "true", "__env": "PLT", "__user": candidate_username}
        response = execute_request(
            self._spec_builder.test_details_spec(), "GET", path_params={"testSlug": test_slug},
            query_params=params, expected_status_code=expected_status_code,
        )
        data = response.json()
        return {"status_code": response.status_code, "test_id": data.get("id"), "sections": data.get("sections") or []}

    def post_test_init(self, test_id: str, candidate_username: str, expected_status_code: int = 201) -> dict[str, Any]:
        """Mirrors post_test_init.py."""
        params = {"__env": "PLT", "__user": candidate_username}
        response = execute_request(
            self._spec_builder.test_init_spec(), "POST", path_params={"testId": test_id}, query_params=params,
            body={"id": test_id}, expected_status_code=expected_status_code,
        )
        data = response.json()
        return {"status_code": response.status_code, "solutionset_id": data.get("testsolutionset_id")}

    def get_infra_allocate(self, solutionset_id: str) -> dict[str, Any]:
        """Mirrors get_infra_allocate.py: polls every 10s for up to 120s until `is_ready` is true."""
        spec = self._spec_builder.infra_allocate_spec()
        max_attempts = 12
        is_ready = False
        response: Optional[requests.Response] = None
        for attempt in range(1, max_attempts + 1):
            response = execute_get_request_without_status_assertion(spec, path_params={"solutionsetId": solutionset_id})
            if response.status_code == 200:
                is_ready = response.json().get("is_ready")
                if is_ready:
                    break
                if attempt < max_attempts:
                    time.sleep(10)
            else:
                raise AssertionError(f"Infra allocation failed with status code: {response.status_code}")
        if not is_ready:
            raise AssertionError(f"Infrastructure not ready after {max_attempts} attempts (120 seconds)")
        return {"status_code": response.status_code}

    def post_test_start(self, test_id: str, candidate_username: str, expected_status_code: int = 201) -> dict[str, Any]:
        """Mirrors post_test_start.py."""
        params = {"__env": "PLT", "__user": candidate_username}
        response = execute_request(
            self._spec_builder.test_start_spec(), "POST", path_params={"testId": test_id}, query_params=params,
            body={"id": test_id}, expected_status_code=expected_status_code,
        )
        return {"status_code": response.status_code}

    def get_sectionwise_problems(self, test_id: str, test_slug: str, expected_status_code: int = 200) -> dict[str, Any]:
        """Mirrors get_sectionwise_problems.py."""
        response = execute_request(
            self._spec_builder.sectionwise_problems_spec(), "GET", path_params={"testId": test_id},
            query_params={"test_slug": test_slug}, expected_status_code=expected_status_code,
        )
        data = response.json()
        return {
            "status_code": response.status_code,
            "problem_slug": data[0]["problems"][0]["slug"],
            "problem_id": data[0]["problems"][0]["id"],
        }

    def get_assessment_problems(
        self, test_id: str, problem_id: str, solution_lang: str, expected_status_code: int = 200
    ) -> dict[str, Any]:
        """Mirrors get_assessment_problems.py."""
        response = execute_request(
            self._spec_builder.assessment_problems_spec(), "GET", path_params={"testId": test_id},
            query_params={"ids": problem_id}, expected_status_code=expected_status_code,
        )
        data = response.json()
        return {"status_code": response.status_code, "problem_stub": data[0]["stubs"][solution_lang]}

    def post_create_solution(
        self,
        solution_type: str,
        candidate_username: str,
        problem_slug: str,
        test_slug: Optional[str],
        solutionset_id: str,
        correct_answer: Optional[list] = None,
        problem_stub: Optional[dict] = None,
        solution_lang: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors post_create_solution.py."""
        payload = get_solution_payload(
            solution_type, candidate_username, problem_slug, test_slug, solutionset_id,
            correct_answer, problem_stub, solution_lang,
        )
        params = {"__env": "PLT", "__user": candidate_username}
        response = execute_request(self._spec_builder.solution_list_spec(), "POST", query_params=params, body=payload)
        if response.status_code not in (200, 201):
            raise AssertionError(f"Expected status code 200 or 201, got {response.status_code}")
        data = response.json()
        return {"status_code": response.status_code, "solution_slug": data["slug"], "solution_id": data["id"]}

    def patch_solution(
        self,
        solution_slug: str,
        solution_type: str,
        test_slug: str,
        correct_answer: Optional[list] = None,
        solution_code: Optional[str] = None,
        solution_lang: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors patch_solution.py. `__user` is RECRUITER_USERNAME in the source, preserved as-is."""
        payload = get_patch_payload(solution_type, test_slug, correct_answer, solution_code, solution_lang)
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.solution_detail_spec(), "PATCH", path_params={"solutionSlug": solution_slug},
            query_params=params, body=payload,
        )
        if response.status_code not in (200, 202):
            raise AssertionError(f"Expected status code 200 or 202, got {response.status_code}")
        return {"status_code": response.status_code}

    def post_code_run(
        self,
        solution_type: str,
        solution_lang: str,
        solution_code: str,
        problem_id: str,
        solution_id: str,
        sock_id: Optional[str],
        candidate_username: str,
    ) -> dict[str, Any]:
        """Mirrors post_code_run.py."""
        params = {"__source": "TST", "verify": "none", "__env": "PLT", "__user": candidate_username, "solution_type": solution_type}
        payload = code_run_payload(solution_lang, solution_code, problem_id, solution_id, sock_id, candidate_username)
        response = execute_request(self._spec_builder.code_run_spec(), "POST", query_params=params, body=payload)
        if response.status_code not in (200, 201):
            raise AssertionError(f"Expected status code 200 or 201, got {response.status_code}")
        return {"status_code": response.status_code}

    def post_submit_solution(
        self,
        solution_id: str,
        sock_id: Optional[str],
        test_slug: Optional[str],
        solution_slug: str,
        candidate_username: str,
        expected_status_code: int = 202,
    ) -> dict[str, Any]:
        """
        Mirrors tests/regression_api_methods/recruit/post_submit_solution.py — candidate-authed
        (see module docstring), hence ported under hacker.
        """
        params = {"__source": "TST", "__env": "PLT", "__user": candidate_username}
        payload = get_submit_solution_payload(solution_id, sock_id, test_slug, solution_slug)
        response = execute_request(
            self._spec_builder.solutions_submit_spec(), "POST", query_params=params, body=payload,
            expected_status_code=expected_status_code,
        )
        return {"status_code": response.status_code}

    def post_test_submit_all(
        self, solutionset_id: str, candidate_username: str, expected_status_code: int = 202
    ) -> dict[str, Any]:
        """Mirrors post_test_submit_all.py."""
        params = {"__env": "PLT", "__user": candidate_username}
        current_time = datetime.now(timezone.utc).isoformat()
        payload = {
            "submission_type": "MSB",
            "proctoring_end_time": current_time,
            "reason": "",
            "testsolutionset_end_time": current_time,
            "websocket_event_sequence": "1",
        }
        response = execute_request(
            self._spec_builder.test_submit_all_spec(), "POST", path_params={"solutionsetId": solutionset_id},
            query_params=params, body=payload, expected_status_code=expected_status_code,
        )
        return {"status_code": response.status_code}

    # -- Socket.IO long-polling handshake (connect_websocket.py) --------------------------------

    @staticmethod
    def _websocket_common_params(
        candidate_username: str, solutionset_id: str, test_id: str, test_slug: Optional[str]
    ) -> dict[str, Any]:
        """Mirrors utils.header_generator.get_websocket_common_params(shared_data)."""
        return {
            "username": candidate_username,
            "contextKey": "user",
            "assessmentType": "test",
            "assessmentId": solutionset_id,
            "testId": test_id,
            "testSlug": test_slug,
            "testDuration": "120",
            "usertype": "hacker",
            "EIO": "4",
            "transport": "polling",
            "t": "PXqwMbx",
        }

    def get_websocket_polling_one(
        self, candidate_username: str, solutionset_id: str, test_id: str, test_slug: Optional[str]
    ) -> dict[str, Any]:
        """Mirrors get_websocket_polling_one.py: merges response cookies into the candidate session."""
        params = self._websocket_common_params(candidate_username, solutionset_id, test_id, test_slug)
        response = execute_request(
            self._spec_builder.websocket_polling_spec(), "GET", query_params=params, expected_status_code=200
        )
        self._session.cookie = _merge_cookie(self._session.cookie, response)
        return {"status_code": response.status_code, "response": response.text}

    def post_websocket_polling(
        self, candidate_username: str, solutionset_id: str, test_id: str, test_slug: Optional[str], sid: Optional[str]
    ) -> dict[str, Any]:
        """Mirrors post_websocket_polling.py: raw "40" Socket.IO CONNECT packet body."""
        params = self._websocket_common_params(candidate_username, solutionset_id, test_id, test_slug)
        params.update({"sid": sid, "t": "PXqwMbx"})
        spec = self._spec_builder.websocket_polling_spec()
        response = requests.post(
            url=spec.base_url.rstrip("/") + spec.base_path, headers=spec.headers, params=params, data="40",
            timeout=spec.timeout_ms / 1000,
        )
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200, got {response.status_code}")
        return {"status_code": response.status_code}

    def get_websocket_polling_two(
        self, candidate_username: str, solutionset_id: str, test_id: str, test_slug: Optional[str], sid: Optional[str]
    ) -> dict[str, Any]:
        """Mirrors get_websocket_polling_two.py."""
        params = self._websocket_common_params(candidate_username, solutionset_id, test_id, test_slug)
        params.update({"sid": sid, "t": "PXqwMbx"})
        response = execute_request(
            self._spec_builder.websocket_polling_spec(), "GET", query_params=params, expected_status_code=200
        )
        return {"status_code": response.status_code, "response": response.text}

    def connect_websocket(
        self, candidate_username: str, solutionset_id: str, test_id: str, test_slug: Optional[str]
    ) -> dict[str, Any]:
        """
        Mirrors connect_websocket.py: runs the three polling calls in order, extracts `sid` (from
        the first GET) and `sock_id` (from the second GET) via get_sid_from_response.
        """
        res1 = self.get_websocket_polling_one(candidate_username, solutionset_id, test_id, test_slug)
        sid = get_sid_from_response(res1["response"])

        res2 = self.post_websocket_polling(candidate_username, solutionset_id, test_id, test_slug, sid)

        res3 = self.get_websocket_polling_two(candidate_username, solutionset_id, test_id, test_slug, sid)
        sock_id = get_sid_from_response(res3["response"])

        ok = res1["status_code"] == 200 and res2["status_code"] == 200 and res3["status_code"] == 200
        return {"status_code": 200 if ok else 400, "sid": sid, "sock_id": sock_id}
