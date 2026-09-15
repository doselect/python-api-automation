"""
Ports tests/regression_api_methods/doiq/*.py (do-api-automation): one method per DoIQ endpoint,
executed through src.core.rest_client.execute_request instead of a raw `requests.get/post` call
+ manual try/except/finally logging — same requests, same status-code assertions, same payload.
The source's `attach_details_to_allure` calls are superseded by execute_request's own Allure
request/response attachment (see src/core/do_api_helpers.py's docstring note).
"""
from __future__ import annotations

from typing import Optional

import requests

from src.core.do_api_config import RECRUITER_USERNAME
from src.core.rest_client import execute_request
from src.specs.doiq_spec_builder import DoiqSpecBuilder


def _conversation_payload(preset: str = "p", input_text: str = "test input") -> dict:
    """Mirrors payloads/regression/doiq/payload_doiq_conversation.py::conversation_payload."""
    return {"preset": preset, "input": input_text}


class DoiqResponseHandler:
    """Wraps a DoiqSpecBuilder to centralize the ported `doiq` regression API calls."""

    def __init__(self, spec_builder: DoiqSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def get_doiq_init(self, context: Optional[str] = None, expected_status_code: int = 200) -> requests.Response:
        """Mirrors get_doiq_init(shared_data, context) — params are `get_doiq_init_params` (always `{"context": "assessment"}` in source, `context` arg is additionally merged in as in the source function)."""
        params = {"context": "assessment"}
        if context:
            params["context"] = context
        return execute_request(
            self._spec_builder.doiq_init_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def get_doiq_roles(self, expected_status_code: int = 200) -> requests.Response:
        """
        Mirrors get_doiq_roles(auth_manager, shared_data). `get_doiq_roles_params` reads
        `shared_data.get("recruiter_username", "shivanshu.tyagi")` — no call site ever sets
        `recruiter_username` in shared_data, so the fallback literal is what always executes;
        preserved as-is rather than swapped for RECRUITER_USERNAME.
        """
        return execute_request(
            self._spec_builder.doiq_roles_spec(), "GET",
            query_params={"__env": "PLT", "__user": "shivanshu.tyagi"},
            expected_status_code=expected_status_code,
        )

    def get_doiq_skills(self, expected_status_code: int = 200) -> requests.Response:
        """Mirrors get_doiq_skills(shared_data)."""
        return execute_request(
            self._spec_builder.doiq_skills_spec(), "GET",
            query_params={"__env": "PLT", "__user": RECRUITER_USERNAME},
            expected_status_code=expected_status_code,
        )

    def get_doiq_responsibilities(self, expected_status_code: int = 200) -> requests.Response:
        """Mirrors get_doiq_responsibilities(shared_data)."""
        return execute_request(
            self._spec_builder.doiq_responsibilities_spec(), "GET",
            query_params={"__env": "PLT", "__user": RECRUITER_USERNAME},
            expected_status_code=expected_status_code,
        )

    def get_doiq_skill_to_skill(
        self, skills: Optional[str] = None, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors get_doiq_skill_to_skill(shared_data, skills)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        if skills:
            params["skills"] = skills
        return execute_request(
            self._spec_builder.doiq_skill_to_skill_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def get_doiq_clear(self, context: Optional[str] = None, expected_status_code: int = 200) -> requests.Response:
        """Mirrors get_doiq_clear(shared_data, context)."""
        params = {}
        if context:
            params["context"] = context
        return execute_request(
            self._spec_builder.doiq_clear_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def post_doiq_conversation(
        self,
        context: Optional[str] = None,
        preset: str = "p",
        input_text: str = "test input",
        expected_status_code: int = 201,
    ) -> requests.Response:
        """Mirrors post_doiq_conversation(shared_data, context, preset, input_text)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        if context:
            params["context"] = context
        return execute_request(
            self._spec_builder.doiq_conversation_post_spec(), "POST", query_params=params,
            body=_conversation_payload(preset, input_text), expected_status_code=expected_status_code,
        )

    def get_doiq_conversation(
        self,
        context: Optional[str] = None,
        preset: Optional[str] = None,
        filesize: Optional[str] = None,
    ) -> requests.Response:
        """
        Mirrors get_doiq_conversation(shared_data, context, preset, filesize). Source asserts 201
        only on the "no interview.summary found" branch (see that function) — status is not
        asserted here either; callers assert as needed, matching that conditional behavior.
        """
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        if context:
            params["context"] = context
        if preset:
            params["preset"] = preset
        if filesize is not None:
            params["filesize"] = filesize
        spec = self._spec_builder.doiq_conversation_get_spec(ai_interview=(context == "interview"))
        return execute_request(spec, "GET", query_params=params)

    def get_all_doiq_conversation_response(self, response: requests.Response) -> dict:
        """
        Mirrors the `interview_name`/`interview_slug` extraction in get_doiq_conversation:
        scans response["result"] for a "interview.summary" template item.
        """
        interview_name = None
        interview_slug = None
        for item in response.json().get("result", []):
            if item.get("template") == "interview.summary":
                data = item.get("message", {}).get("content", {}).get("data", {})
                interview_name = data.get("name")
                interview_slug = data.get("assessment_slug")
                break
        return {"interview_name": interview_name, "interview_slug": interview_slug}
