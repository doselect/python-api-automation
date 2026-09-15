"""
Ports the `api_helper.make_request(...)` call sites in tests/public_apis/invite/*.py
(do-api-automation), mirroring ProblemsResponseHandler's convention.
"""
from __future__ import annotations

from typing import Any, Optional
from urllib.parse import parse_qs, urlparse

import requests

from src.core.rest_client import execute_request
from src.specs.invite_spec_builder import InviteSpecBuilder


class InviteResponseHandler:
    """Wraps an InviteSpecBuilder to centralize the ported `invite` public API calls."""

    def __init__(self, spec_builder: InviteSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def get_all_tests(self, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/test (test_get_all_test.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_list"), "GET", expected_status_code=expected_status_code
        )

    def get_one_test(self, test_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/test/{testSlug} (test_get_one_test.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_detail"), "GET",
            path_params={"testSlug": test_slug}, expected_status_code=expected_status_code,
        )

    def get_all_candidates_of_test(self, test_slug: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET .../candidates (test_get_all_candidates_of_test.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidates"), "GET",
            path_params={"testSlug": test_slug}, expected_status_code=expected_status_code,
        )

    def create_invite(
        self, test_slug: str, payload: dict[str, Any], expected_status_code: int = 201
    ) -> requests.Response:
        """Mirrors POST .../candidates?suppress_email=true (conftest.create_invite)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidates"), "POST",
            path_params={"testSlug": test_slug}, body=payload,
            query_params={"suppress_email": "true"}, expected_status_code=expected_status_code,
        )

    def post_bulk_invite_candidate(
        self, test_slug: str, payload: dict[str, Any], expected_status_code: int = 202
    ) -> requests.Response:
        """Mirrors POST .../candidates/bulk/ (test_post_bulk_invite_candidate.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidates_bulk"), "POST",
            path_params={"testSlug": test_slug}, body=payload, expected_status_code=expected_status_code,
        )

    def update_invite_candidate(
        self, test_slug: str, candidate_email: str, payload: dict[str, Any], expected_status_code: int = 202
    ) -> requests.Response:
        """Mirrors PATCH .../candidates/{candidateEmail}?suppress_email=True (test_update_invite_candidate.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_detail"), "PATCH",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email}, body=payload,
            query_params={"suppress_email": "True"}, expected_status_code=expected_status_code,
        )

    def delete_invite_candidate(
        self, test_slug: str, candidate_email: str, expected_status_code: int = 204
    ) -> requests.Response:
        """Mirrors DELETE .../candidates/{candidateEmail}?suppress_email=True (test_delete_invite_candidate.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_detail"), "DELETE",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email}, body={},
            query_params={"suppress_email": "True"}, expected_status_code=expected_status_code,
        )

    def add_retakes_candidate(
        self, test_slug: str, candidate_email: str, payload: dict[str, Any], expected_status_code: int = 201
    ) -> requests.Response:
        """Mirrors POST .../candidates/{candidateEmail}/retake (test_add_retakes_candidate.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_retake"), "POST",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email}, body=payload,
            expected_status_code=expected_status_code,
        )

    def extend_invite_candidate(
        self, test_slug: str, candidate_email: str, payload: dict[str, Any], expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors POST .../candidates/{candidateEmail}/extend_duration?suppress_email=True (test_extend_invite_candidate.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_extend_duration"), "POST",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email}, body=payload,
            query_params={"suppress_email": "True"}, expected_status_code=expected_status_code,
        )

    def get_candidate_past_reports(
        self, test_slug: str, candidate_email: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors GET .../candidates/{candidateEmail}/past_reports (test_get_candidate_past_reports.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_past_reports"), "GET",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email},
            expected_status_code=expected_status_code,
        )

    def get_candidate_report(
        self, test_slug: str, candidate_email: str, expected_status_code: int = 200
    ) -> requests.Response:
        """Mirrors GET .../candidates/{candidateEmail}/report (test_get_candidate_report.py)."""
        return execute_request(
            self._spec_builder.get_spec("test_candidate_report"), "GET",
            path_params={"testSlug": test_slug, "candidateEmail": candidate_email},
            expected_status_code=expected_status_code,
        )

    def get_candidate_all_invites(self, email: str, expected_status_code: int = 200) -> requests.Response:
        """Mirrors GET /platform/v1/invite/?email=... (test_get_candidate_all_invites.py)."""
        return execute_request(
            self._spec_builder.get_spec("invite_list"), "GET",
            query_params={"email": email}, expected_status_code=expected_status_code,
        )

    def post_invite_candidate_and_get_access_code(
        self, test_slug: str, payload: dict[str, Any], expected_status_code: int = 201
    ) -> tuple[requests.Response, Optional[str]]:
        """
        Mirrors tests/public_apis/invite/post_invite_candidate.py's `post_invite_candidate` helper
        (used by the hacker-domain attempt flows, not a test itself): creates an invite and
        extracts `access_code` from the returned `candidate_access_url` query string.
        """
        response = self.create_invite(test_slug, payload, expected_status_code)
        access_code = None
        if response.status_code == expected_status_code:
            access_url = response.json().get("candidate_access_url")
            if access_url:
                access_code = parse_qs(urlparse(access_url).query).get("access_code", [None])[0]
        return response, access_code
