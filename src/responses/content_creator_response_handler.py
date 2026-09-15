"""
Ports tests/regression_api_methods/content_creator/*.py (do-api-automation): one method per
endpoint, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (see doiq_response_handler.py's docstring — same rationale).
"""
from __future__ import annotations

from typing import Optional

import requests

from src.core.do_api_config import CREATOR_USERNAME
from src.core.rest_client import execute_request
from src.helpers.content_creator.payloads import (
    create_problem_payload,
    get_creator_stats_payload,  # noqa: F401 — mirrors source: built but never sent (see method docstring)
    patch_problem_content_creator_payload,
    patch_problem_reviewer_payload,
    patch_problem_status_creator_payload,
    resolve_creator_username,
    set_problem_status_reviewer_payload,
)
from src.specs.content_creator_spec_builder import ContentCreatorSpecBuilder


def _extract_etag(response: requests.Response) -> Optional[str]:
    """Mirrors the `response.headers.get("ETag", "").strip('"').replace(';gzip', '')` extraction."""
    etag = response.headers.get("ETag", "").strip('"').replace(";gzip", "")
    return etag or None


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
