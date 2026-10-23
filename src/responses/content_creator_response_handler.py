"""
Ports tests/regression_api_methods/content_creator/*.py (do-api-automation): one method per
endpoint, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (see doiq_response_handler.py's docstring — same rationale).
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable, Optional

import requests

from src.core.do_api_config import CREATOR_USERNAME
from src.core.rest_client import execute_request
from src.helpers.content_creator.payloads import (
    create_problem_payload,
    create_scr_problem_payload,
    get_creator_stats_payload,  # noqa: F401 — mirrors source: built but never sent (see method docstring)
    patch_problem_content_creator_payload,
    patch_problem_reviewer_payload,
    patch_problem_status_creator_payload,
    resolve_creator_username,
    set_problem_status_reviewer_payload,
    testcase_payload,
)
from src.specs.content_creator_spec_builder import ContentCreatorSpecBuilder


def _extract_etag(response: requests.Response) -> Optional[str]:
    """Mirrors the `response.headers.get("ETag", "").strip('"').replace(';gzip', '')` extraction."""
    etag = response.headers.get("ETag", "").strip('"').replace(";gzip", "")
    return etag or None


def _problem_params(problem_slug: str, username: str) -> dict:
    """Query params the creator problem page sends on problem / testcase / problemcheck calls."""
    return {
        "__env": "PLT", "__user": username, "_role": "ADM", "limit": 20, "offset": 0,
        "problem__slug": problem_slug,
    }


def _wait_until(
    fetch: Callable[[], Any], is_done: Callable[[Any], bool], what: str,
    timeout_seconds: int = 180, poll_seconds: int = 5,
) -> Any:
    """Polls `fetch` until `is_done(result)` is true and returns that result; fails after `timeout_seconds`."""
    deadline = time.monotonic() + timeout_seconds
    while True:
        body = fetch()
        if is_done(body):
            return body
        if time.monotonic() > deadline:
            raise AssertionError(f"{what} not finished after {timeout_seconds}s, last response: {body}")
        time.sleep(poll_seconds)


class ContentCreatorResponseHandler:
    """Wraps a ContentCreatorSpecBuilder to centralize the ported `content_creator` calls."""

    def __init__(self, spec_builder: ContentCreatorSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def get_creator_stats(self, expected_status_code: int = 200) -> requests.Response:
        """
        Mirrors get_creator_stats.py::get_creator_stats(shared_data). `params` is `{}` there
        ("get_creator_stats" isn't one of generate_params's named cases, so it falls to the
        default `{}`); `get_creator_stats_payload()` is likewise built but never actually sent
        (a GET call) — both preserved as no-ops here for fidelity.
        """
        return execute_request(
            self._spec_builder.creator_stats_spec(), "GET", expected_status_code=expected_status_code
        )

    def post_create_problem(self, username: str, expected_status_code: int = 201) -> str:
        """
        Mirrors post_create_problem.py::post_create_problem(shared_data): returns the created
        problem's slug directly (source stashed it in `shared_data["problem_slug"]`).
        """
        params = {"__env": "PLT", "__user": username}
        response = execute_request(
            self._spec_builder.problem_list_spec(), "POST", query_params=params,
            body=create_problem_payload(username), expected_status_code=expected_status_code,
        )
        return response.json()["slug"]

    def patch_problem_content_creator(
        self, problem_slug: str, username: str, expected_status_code: int = 202
    ) -> requests.Response:
        """Mirrors patch_problem_content_creator.py::patch_problem_content_creator_api(shared_data)."""
        params = {
            "__env": "PLT", "__user": username, "_role": "ADM", "limit": 20, "offset": 0,
            "problem__slug": problem_slug,
        }
        get_response = execute_request(
            self._spec_builder.problem_detail_get_spec(), "GET",
            path_params={"problemSlug": problem_slug}, query_params=params,
        )
        etag = _extract_etag(get_response) if get_response.status_code == 200 else None

        return execute_request(
            self._spec_builder.problem_detail_patch_spec(problem_slug, etag), "PATCH",
            path_params={"problemSlug": problem_slug}, query_params=params,
            body=patch_problem_content_creator_payload(problem_slug),
            expected_status_code=expected_status_code,
        )

    def patch_problem_status_creator(self, problem_slug: str, username: str) -> requests.Response:
        """
        Mirrors patch_problem_status_creator.py::patch_problem_status_creator_api(shared_data):
        the GET-for-ETag call always uses CREATOR_USERNAME (not the resolved `username`) — an
        inconsistency in the source, preserved here rather than "fixed". Asserts 200 or 202
        (source's own `assert ... in [200, 202]`), so no single `expected_status_code` is passed
        to execute_request for the PATCH.
        """
        get_params = {
            "__env": "PLT", "__user": CREATOR_USERNAME, "_role": "ADM", "limit": 20, "offset": 0,
            "problem__slug": problem_slug,
        }
        get_response = execute_request(
            self._spec_builder.problem_detail_get_spec(), "GET",
            path_params={"problemSlug": problem_slug}, query_params=get_params,
        )
        etag = _extract_etag(get_response) if get_response.status_code == 200 else None

        patch_params = {
            "__env": "PLT", "__user": username, "_role": "ADM", "limit": 20, "offset": 0,
            "problem__slug": problem_slug,
        }
        response = execute_request(
            self._spec_builder.problem_detail_patch_spec(problem_slug, etag), "PATCH",
            path_params={"problemSlug": problem_slug}, query_params=patch_params,
            body=patch_problem_status_creator_payload(),
        )
        assert response.status_code in (200, 202), (
            f"Expected status code 200 or 202, got {response.status_code}"
        )
        return response

    def post_create_scr_problem(self, username: str, expected_status_code: int = 201) -> requests.Response:
        """POST /api/v1/problem — creates a scripting (SCR) problem and returns the full response."""
        return execute_request(
            self._spec_builder.problem_list_spec(), "POST", query_params={"__env": "PLT", "__user": username},
            body=create_scr_problem_payload(username), expected_status_code=expected_status_code,
        )

    def get_problem(self, problem_slug: str, username: str, expected_status_code: int = 200) -> requests.Response:
        """GET /api/v1/problem/{problemSlug}"""
        return execute_request(
            self._spec_builder.problem_detail_get_spec(), "GET", path_params={"problemSlug": problem_slug},
            query_params=_problem_params(problem_slug, username), expected_status_code=expected_status_code,
        )

    def patch_problem(
        self, problem_slug: str, username: str, body: dict, expected_status_code: int = 202
    ) -> requests.Response:
        """PATCH /api/v1/problem/{problemSlug} — partial update with whatever fields `body` carries."""
        return execute_request(
            self._spec_builder.problem_detail_patch_spec(problem_slug, etag=None), "PATCH",
            path_params={"problemSlug": problem_slug}, query_params=_problem_params(problem_slug, username),
            body=body, expected_status_code=expected_status_code,
        )

    def get_creator_stats_getter(self, username: str, expected_status_code: int = 200) -> requests.Response:
        """GET /rpc/creator/getter.creator_stats"""
        params = {"__env": "PLT", "__user": username, "creator_username": username}
        return execute_request(
            self._spec_builder.creator_stats_getter_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def post_generate_solution(
        self, problem_slug: str, username: str, languages: list[str], expected_status_code: int
    ) -> requests.Response:
        """
        POST /rpc/problems.generate_solution/ — AI sample-solution generation. No default status: only
        the AI-service-down response (502) has been captured so far, so callers must state what they expect.
        """
        return execute_request(
            self._spec_builder.generate_solution_spec(problem_slug), "POST",
            query_params={"__env": "PLT", "__user": username},
            body={"problem_slug": problem_slug, "languages": languages}, expected_status_code=expected_status_code,
        )

    def search_tags(self, query: str, expected_status_code: int = 200) -> requests.Response:
        """GET /search/search?index=tag"""
        params = {"index": "tag", "limit": 15, "offset": 0, "page_type": "", "q": query, "tag": "", "view": ""}
        return execute_request(
            self._spec_builder.tag_search_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def get_problem_comments(
        self, problem_slug: str, username: str, expected_status_code: int = 200
    ) -> requests.Response:
        """GET /api/v1/problemcomment"""
        params = {"__env": "PLT", "__user": username, "problem__slug": problem_slug}
        return execute_request(
            self._spec_builder.problem_comment_list_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def get_problem_testcases(
        self, problem_slug: str, username: str, expected_status_code: int = 200
    ) -> requests.Response:
        """GET /api/v1/problemtestcase"""
        return execute_request(
            self._spec_builder.problem_testcase_list_spec(), "GET",
            query_params=_problem_params(problem_slug, username), expected_status_code=expected_status_code,
        )

    def get_solution_status(
        self, problem_slug: str, username: str, expected_status_code: int = 200
    ) -> requests.Response:
        """GET /rpc/problems.solution_status"""
        params = {"problem_slug": problem_slug, "__env": "PLT", "__user": username}
        return execute_request(
            self._spec_builder.problem_solution_status_spec(problem_slug), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def get_code_stub_configuration(
        self, problem_slug: str, problem_type: str, expected_status_code: int = 200
    ) -> requests.Response:
        """GET /code-stub-generator/configuration/"""
        return execute_request(
            self._spec_builder.code_stub_configuration_spec(problem_slug), "GET",
            query_params={"problem_type": problem_type}, expected_status_code=expected_status_code,
        )

    def get_online_plagiarism_data(
        self, problem_slug: str, username: str, expected_status_code: int = 200
    ) -> requests.Response:
        """GET /rpc/online_plagiarism_data/{problemSlug}"""
        return execute_request(
            self._spec_builder.online_plagiarism_data_spec(problem_slug), "GET",
            path_params={"problemSlug": problem_slug}, query_params={"__env": "PLT", "__user": username},
            expected_status_code=expected_status_code,
        )

    def get_problem_check(
        self, problem_slug: str, username: str, expected_status_code: int = 404
    ) -> requests.Response:
        """GET /api/v1/problem/{problemSlug}/problemcheck — 404 until a check has been run on the problem."""
        return execute_request(
            self._spec_builder.problem_check_spec(problem_slug), "GET", path_params={"problemSlug": problem_slug},
            query_params=_problem_params(problem_slug, username), expected_status_code=expected_status_code,
        )

    def create_testcase(
        self, problem_slug: str, username: str, testcase: dict, expected_status_code: int = 201
    ) -> requests.Response:
        """POST /api/v1/problemtestcase"""
        return execute_request(
            self._spec_builder.problem_testcase_list_spec(), "POST",
            query_params=_problem_params(problem_slug, username),
            body=testcase_payload(testcase, problem_slug, username), expected_status_code=expected_status_code,
        )

    def start_sanity_check(self, problem_slug: str, username: str, sockmeta: dict) -> requests.Response:
        """
        POST /api/v1/problem/{problemSlug}/problemcheck. `sockmeta` is always sent: without it d6 answers 500
        (KeyError 'sockmeta' — happens when the dashboard's websocket is down). d6 returns 201; 200 is also
        accepted since prod is reported to answer 200.
        """
        response = execute_request(
            self._spec_builder.problem_check_spec(problem_slug), "POST", path_params={"problemSlug": problem_slug},
            query_params={"__env": "PLT", "__user": username}, body={"sockmeta": sockmeta},
        )
        assert response.status_code in (200, 201), f"Expected 200 or 201, got {response.status_code}: {response.text}"
        return response

    def wait_for_solution_generation(self, problem_slug: str, username: str) -> dict:
        """Polls GET /rpc/problems.solution_status until AI generation reports `Generated`."""
        return _wait_until(
            lambda: self.get_solution_status(problem_slug, username).json(),
            lambda body: body["scr_solution_status"] == "Generated", "AI solution generation",
        )

    def wait_for_sanity_check(self, problem_slug: str, username: str) -> dict:
        """Polls GET /api/v1/problem/{problemSlug}/problemcheck until the check leaves `PEN` (pending)."""
        return _wait_until(
            lambda: self.get_problem_check(problem_slug, username, expected_status_code=200).json(),
            lambda body: body["status"] != "PEN", "Sanity check",
        )

    def upload_mcq_bulk_file(self, csv_path: Path, username: str, expected_status_code: int = 200) -> requests.Response:
        """POST /rpc/problems.mcq_upload_bulk/v2 (multipart) — validates the CSV and returns the stored `filename`."""
        with csv_path.open("rb") as file:
            return execute_request(
                self._spec_builder.mcq_upload_bulk_spec(multipart=True), "POST",
                query_params={"problem_type": "MCQ", "__env": "PLT", "__user": username},
                files={"file": (csv_path.name, file, "text/csv")}, expected_status_code=expected_status_code,
            )

    def confirm_mcq_bulk_upload(
        self, filename: str, username: str, auto_approval: bool, expected_status_code: int = 200
    ) -> requests.Response:
        """
        POST /rpc/problems.mcq_upload_bulk/v2?state=confirmation — creates the problems in the background.
        `auto_approval=False` is the dashboard's Draft checkbox ticked; True uploads them as Approved.
        """
        params = {
            "__env": "PLT", "__user": username, "auto_approval": str(auto_approval).lower(), "filename": filename,
            "problem_type": "MCQ", "state": "confirmation",
        }
        return execute_request(
            self._spec_builder.mcq_upload_bulk_spec(), "POST", query_params=params, body={},
            expected_status_code=expected_status_code,
        )

    def search_problems(self, name: str, username: str, expected_status_code: int = 200) -> requests.Response:
        """GET /api/v1/problem?name__icontains=<name>"""
        params = {
            "__env": "PLT", "__user": username, "_role": "ADM", "limit": 50, "offset": 0, "name__icontains": name,
        }
        return execute_request(
            self._spec_builder.problem_list_spec(), "GET", query_params=params,
            expected_status_code=expected_status_code,
        )

    def wait_for_bulk_uploaded_problems(self, names: list[str], job_id: str, username: str) -> dict[str, dict]:
        """
        Polls until every name has a problem created by this upload, matched on `evaluation_data` carrying the
        upload's `evaluation_job_id` — older problems with the same name are ignored. Returns {name: problem}.
        """
        def fetch() -> dict[str, dict]:
            found = {}
            for name in names:
                for problem in self.search_problems(name, username).json()["objects"]:
                    if problem["name"] == name and job_id in str(problem.get("evaluation_data")):
                        found[name] = problem
            return found

        return _wait_until(fetch, lambda found: len(found) == len(names), "Bulk MCQ upload", timeout_seconds=300)

    def patch_problem_reviewer(self, problem_slug: str, expected_status_code: int = 202) -> requests.Response:
        """Mirrors patch_problem_reviewer.py::patch_problem_reviewer_api(shared_data) (params `{}`)."""
        return execute_request(
            self._spec_builder.moderation_set_status_spec(), "POST",
            body=patch_problem_reviewer_payload(problem_slug), expected_status_code=expected_status_code,
        )

    def post_set_problem_status_reviewer(
        self, problem_slug: str, expected_status_code: int = 202
    ) -> requests.Response:
        """Mirrors post_set_problem_status_reviewer.py::post_set_problem_status_reviewer(shared_data) (params `{}`)."""
        return execute_request(
            self._spec_builder.moderation_set_status_spec(), "POST",
            body=set_problem_status_reviewer_payload(problem_slug), expected_status_code=expected_status_code,
        )
