"""
Ports the header-building side of tests/regression_api_methods/content_creator/*.py
(do-api-automation). Two roles are involved — content-creator/moderator (creates and edits the
problem) and reviewer/moderator (approves it) — so this spec builder takes two AuthManagers,
matching how tests/test_regression/test_creator/*.py logs in twice (once per role; the moderator
flow logs in as the same account for both).
"""
from __future__ import annotations

from src.constants.paths import content_creator_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.specs.session_auth_headers import default_content_creator_headers, default_reviewer_headers


class ContentCreatorSpecBuilder:
    """Builds the reusable request specs for the ported `content_creator` regression endpoints."""

    def __init__(self, creator_auth_manager: AuthManager, reviewer_auth_manager: AuthManager) -> None:
        self._creator_auth_manager = creator_auth_manager
        self._reviewer_auth_manager = reviewer_auth_manager

    def creator_stats_spec(self) -> RequestSpec:
        """Mirrors get_creator_stats.py's headers (plain default content-creator headers)."""
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=content_creator_api_path.CREATOR_STATS,
            headers=default_content_creator_headers(self._creator_auth_manager),
        )

    def problem_list_spec(self) -> RequestSpec:
        """Mirrors post_create_problem.py's headers (plain default content-creator headers)."""
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=content_creator_api_path.PROBLEM_LIST,
            headers=default_content_creator_headers(self._creator_auth_manager),
        )

    def problem_detail_get_spec(self) -> RequestSpec:
        """Mirrors the ETag-fetching GET in patch_problem_content_creator.py/patch_problem_status_creator.py."""
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=content_creator_api_path.PROBLEM_DETAIL,
            headers=default_content_creator_headers(self._creator_auth_manager),
        )

    def problem_detail_patch_spec(self, problem_slug: str, etag: str | None) -> RequestSpec:
        """
        Mirrors the PATCH headers in patch_problem_content_creator.py/patch_problem_status_creator.py:
        default content-creator headers, `referer` pointed at the specific problem page, and an
        `if-match` header when an ETag was retrieved.
        """
        headers = default_content_creator_headers(self._creator_auth_manager)
        headers["referer"] = f"{content_creator_api_path.set_base_url()}/creator/problem/{problem_slug}"
        if etag:
            headers["if-match"] = f'"{etag};gzip"'
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=content_creator_api_path.PROBLEM_DETAIL,
            headers=headers,
        )

    def _problem_page_spec(self, base_path: str, problem_slug: str) -> RequestSpec:
        """Default content-creator headers with `referer` pointed at the problem page (as the dashboard sends)."""
        headers = default_content_creator_headers(self._creator_auth_manager)
        headers["referer"] = f"{content_creator_api_path.set_base_url()}/creator/problem/{problem_slug}"
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=base_path, headers=headers,
        )

    def _creator_spec(self, base_path: str) -> RequestSpec:
        """Plain default content-creator headers for `base_path`."""
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(), base_path=base_path,
            headers=default_content_creator_headers(self._creator_auth_manager),
        )

    def problem_comment_list_spec(self) -> RequestSpec:
        return self._creator_spec(content_creator_api_path.PROBLEM_COMMENT_LIST)

    def problem_testcase_list_spec(self) -> RequestSpec:
        return self._creator_spec(content_creator_api_path.PROBLEM_TESTCASE_LIST)

    def creator_stats_getter_spec(self) -> RequestSpec:
        return self._creator_spec(content_creator_api_path.CREATOR_STATS_GETTER)

    def tag_search_spec(self) -> RequestSpec:
        return self._creator_spec(content_creator_api_path.TAG_SEARCH)

    def mcq_upload_bulk_spec(self, multipart: bool = False) -> RequestSpec:
        """Bulk MCQ upload. The file step is multipart, so its JSON content-type header is dropped."""
        spec = self._creator_spec(content_creator_api_path.MCQ_UPLOAD_BULK)
        if multipart:
            spec.headers.pop("content-type", None)
        return spec

    def problem_solution_status_spec(self, problem_slug: str) -> RequestSpec:
        return self._problem_page_spec(content_creator_api_path.PROBLEM_SOLUTION_STATUS, problem_slug)

    def code_stub_configuration_spec(self, problem_slug: str) -> RequestSpec:
        return self._problem_page_spec(content_creator_api_path.CODE_STUB_CONFIGURATION, problem_slug)

    def online_plagiarism_data_spec(self, problem_slug: str) -> RequestSpec:
        return self._problem_page_spec(content_creator_api_path.ONLINE_PLAGIARISM_DATA, problem_slug)

    def problem_check_spec(self, problem_slug: str) -> RequestSpec:
        return self._problem_page_spec(content_creator_api_path.PROBLEM_CHECK, problem_slug)

    def generate_solution_spec(self, problem_slug: str) -> RequestSpec:
        return self._problem_page_spec(content_creator_api_path.GENERATE_SOLUTION, problem_slug)

    def moderation_set_status_spec(self) -> RequestSpec:
        """Mirrors patch_problem_reviewer.py/post_set_problem_status_reviewer.py's headers (default reviewer headers)."""
        return build_request_spec(
            base_url=content_creator_api_path.set_base_url(),
            base_path=content_creator_api_path.MODERATION_SET_PROBLEM_STATUS,
            headers=default_reviewer_headers(self._reviewer_auth_manager),
        )
