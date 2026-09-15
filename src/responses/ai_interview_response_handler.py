"""
Ports tests/regression_api_methods/ai_interview/*.py (do-api-automation): one method per
endpoint, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (see doiq_response_handler.py's docstring — same rationale).
"""
from __future__ import annotations

import time
from typing import Any, Optional

import requests

from src.core.do_api_config import RECRUITER_USERNAME
from src.core.do_api_helpers import generate_fake_name, generate_random_email
from src.core.rest_client import execute_request
from src.helpers.ai_interview.payloads import (
    ai_interview_jd_extraction_payload,
    get_bulk_invite_payload,
    get_invite_payload,
    post_jd_data_payload,
)
from src.specs.ai_interview_spec_builder import AiInterviewSpecBuilder


class AiInterviewResponseHandler:
    """Wraps an AiInterviewSpecBuilder to centralize the ported `ai_interview` regression calls."""

    def __init__(self, spec_builder: AiInterviewSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def get_dashboard_analytics(self, expected_status_code: int = 200) -> requests.Response:
        """Mirrors get_dashboard_analytics(shared_data)."""
        return execute_request(
            self._spec_builder.dashboard_analytics_spec(), "GET", expected_status_code=expected_status_code
        )

    def get_latest_ai_interview(
        self,
        limit: int = 10,
        offset: int = 0,
        order_by: str = "-created",
        narrow: Optional[str] = None,
        expected_status_code: int = 200,
    ) -> str:
        """
        Mirrors get_latest_ai_interview(shared_data, limit, offset, order_by, narrow): returns the
        `objects[0]["objects"][0]["slug"]` from the search response directly (source stashed it in
        `shared_data["latest_ai_interview_slug"]`).
        """
        if narrow is None:
            narrow = "category|PRI||test_type|GEN||mode|TIM||archived|false||sub_test_type|INT"
        params = {"index": "test", "order_by": order_by, "narrow": narrow, "limit": limit, "offset": offset}
        response = execute_request(
            self._spec_builder.latest_ai_interview_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )
        return response.json()["objects"][0]["objects"][0]["slug"]

    def post_bulk_invite(
        self, slug: str, email_list: Optional[list] = None, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors post_bulk_invite.py::post_invite(shared_data, slug)."""
        if email_list is None:
            email_list = [
                {"email": generate_random_email(), "name": generate_fake_name()},
                {"email": generate_random_email(), "name": generate_fake_name()},
            ]
        payload = get_bulk_invite_payload(slug, email_list)
        return execute_request(
            self._spec_builder.bulk_invite_spec(), "POST", body=payload, expected_status_code=expected_status_code
        )

    def post_invite_ai_interview(
        self, slug: str, email_list: Optional[list] = None, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors post_invite_ai_interview.py::post_invite_ai_interview(shared_data, slug, email_list)."""
        if email_list is None:
            email_list = [
                {"email": generate_random_email(), "name": generate_fake_name()} for _ in range(5)
            ]
        payload = get_bulk_invite_payload(slug, email_list)
        return execute_request(
            self._spec_builder.invite_ai_interview_spec(slug), "POST", body=payload,
            expected_status_code=expected_status_code,
        )

    def post_bulk_invite_no_cv(self, slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors post_bulk_invite_no_cv.py::post_bulk_invite_candidate_invite_no_cv(shared_data, slug)."""
        email_list = [
            {"email": generate_random_email(), "name": generate_fake_name()},
            {"email": generate_random_email(), "name": generate_fake_name()},
        ]
        payload = get_bulk_invite_payload(slug, email_list)
        return execute_request(
            self._spec_builder.bulk_invite_no_cv_spec(slug), "POST", body=payload,
            expected_status_code=expected_status_code,
        )

    def post_single_invite_no_cv(self, slug: str, expected_status_code: int = 201) -> requests.Response:
        """Mirrors post_single_invite_no_cv.py::post_doiq_ai_single_candidate_invite_no_cv(shared_data, slug)."""
        params = {"context": "interview-report", "slug": slug, "__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = get_invite_payload(generate_random_email())
        return execute_request(
            self._spec_builder.doiq_conversation_report_spec(slug), "POST", query_params=params, body=payload,
            expected_status_code=expected_status_code,
        )

    def get_doiq_conversation_ai_interview(
        self,
        preset: Optional[str] = None,
        filesize: Optional[str] = None,
        expected_status_code: int = 201,
        max_polls: int = 6,
        poll_interval_seconds: float = 5.0,
    ) -> dict:
        """
        Mirrors get_ai_interview_doiq_conversation.py::get_doiq_conversation_ai_interview
        (context="interview" is implicit — this is always the interview-context GET). Returns the
        payload for the *next* `post_doiq_conversation_ai_interview` call directly, replacing the
        source's `shared_data["extracted_jd_response"]`/`["post_extracted_jd_response"]` handoff.

        The preceding `post_doiq_conversation_jobdesc`/`_followup` POST runs asynchronously
        server-side — its own response carries `"action": "POLL"` — so a single GET right after can
        still see an empty `message: {}` for the target preset. Polls up to `max_polls` times
        (`poll_interval_seconds` apart) for the `interview.edit` template to show up before giving
        up and raising the last `ai_interview_jd_extraction_payload` error (verified live: the
        source's fixed single-`sleep()`-then-GET pattern intermittently 400s/parses-empty on PLT for
        exactly this reason).
        """
        query_params: dict[str, Any] = {"context": "interview", "preset": preset, "filesize": filesize}
        last_error: Optional[ValueError] = None
        for attempt in range(max_polls):
            response = execute_request(
                self._spec_builder.doiq_conversation_ai_interview_spec(), "GET", query_params=query_params,
                expected_status_code=expected_status_code,
            )
            try:
                return ai_interview_jd_extraction_payload(response.json())
            except ValueError as exc:
                last_error = exc
                if attempt < max_polls - 1:
                    time.sleep(poll_interval_seconds)
        raise last_error

    def post_doiq_conversation_ai_interview(
        self, next_payload: Optional[dict] = None, expected_status_code: int = 201
    ) -> requests.Response:
        """
        Mirrors post_doiq_convorsation.py::post_doiq_conversation_ai_interview(shared_data): body
        is `shared_data.get("post_extracted_jd_response")` there — `None` when nothing populated
        it first (test_post_doiq_conversation.py calls this standalone, so `next_payload` defaults
        to `None` here too, matching that call site's actual behavior).

        `context: "interview"` is required here — without it the backend 400s with "Test matching
        query does not exist." (verified live against PLT); confirmed by mirroring the sibling
        `doiq` domain's `post_doiq_conversation(context="assessment", ...)`, which already sends its
        own `context` and succeeds.
        """
        params = {"context": "interview", "__env": "PLT", "__user": RECRUITER_USERNAME}
        return execute_request(
            self._spec_builder.doiq_conversation_ai_interview_spec(), "POST", query_params=params,
            body=next_payload, expected_status_code=expected_status_code,
        )

    def post_doiq_conversation_followup(
        self, preset: Optional[str] = None, expected_status_code: int = 201
    ) -> requests.Response:
        """
        Mirrors post_doiq_followup.py::post_doiq_conversation_followup(shared_data, preset, ai_follow_up).
        `context: "interview"` added — see post_doiq_conversation_ai_interview's docstring.
        """
        params = {"context": "interview", "__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = {"preset": preset, "ai_follow_up": True, "is_cv_questions_enabled": False}
        return execute_request(
            self._spec_builder.doiq_conversation_ai_interview_spec(), "POST", query_params=params, body=payload,
            expected_status_code=expected_status_code,
        )

    def post_doiq_conversation_jobdesc(self, expected_status_code: int = 201) -> requests.Response:
        """
        Mirrors post_doiq_jd.py::post_doiq_conversation_jobdesc(shared_data).
        `context: "interview"` added — see post_doiq_conversation_ai_interview's docstring.
        """
        params = {"context": "interview", "__env": "PLT", "__user": RECRUITER_USERNAME}
        return execute_request(
            self._spec_builder.doiq_conversation_ai_interview_spec(), "POST", query_params=params,
            body=post_jd_data_payload(), expected_status_code=expected_status_code,
        )

    def post_upload_file(
        self,
        file_path: str,
        upload_type: str = "generic",
        filename_prefix: str = "test/undefined.pdf",
        name: str = "SDET.pdf",
        source: str = "interview",
        file_size: str = "56.8 KB",
        expected_status_code: int = 200,
    ) -> requests.Response:
        """
        Mirrors post_upload_file.py::post_upload_file(shared_data, file_path, ...) — multipart
        upload, so this bypasses execute_request's `json=` body (requests needs `files=`/`data=`
        separately) and calls `requests` directly against the resolved spec URL/headers.
        """
        import requests as _requests  # local import: this is the one call site needing raw requests

        spec = self._spec_builder.upload_file_spec()
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        with open(file_path, "rb") as file_handle:
            files = {"file": (name, file_handle, "application/pdf")}
            data = {
                "upload_type": upload_type,
                "filename_prefix": filename_prefix,
                "name": name,
                "source": source,
                "file_size": file_size,
            }
            response = _requests.post(
                url=spec.base_url.rstrip("/") + spec.base_path,
                headers=spec.headers,
                params=params,
                files=files,
                data=data,
                timeout=spec.timeout_ms / 1000,
            )
        if response.status_code != expected_status_code:
            raise AssertionError(f"Expected status code {expected_status_code}, got {response.status_code}")
        return response
