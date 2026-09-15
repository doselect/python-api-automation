"""
Ports the request-building side of tests/public_apis/problems/*.py (do-api-automation): every
call there builds the same `{"DoSelect-Api-Key": ..., "DoSelect-Api-Secret": ...}` headers dict
inline via utils.config — this spec builder centralizes that into one reusable spec per endpoint,
following this repo's SalariesSpecBuilder convention.
"""
from __future__ import annotations

from typing import Optional

from src.constants.headers.header_constants import HeaderConstants
from src.constants.paths import problems_api_path
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.core.do_api_config import DOSELECT_API_KEY, DOSELECT_API_SECRET


def get_problems_headers() -> dict[str, str]:
    """Mirrors the inline `headers = {"DoSelect-Api-Key": ..., "DoSelect-Api-Secret": ...}` dict."""
    return {
        HeaderConstants.DOSELECT_API_KEY_HEADER: DOSELECT_API_KEY,
        HeaderConstants.DOSELECT_API_SECRET_HEADER: DOSELECT_API_SECRET,
    }


class ProblemsSpecBuilder:
    """Builds and holds the reusable request specs for the ported `problems` public API tests."""

    def __init__(self) -> None:
        self._specs: dict[str, RequestSpec] = {}

    def _spec_for(self, key: str, base_path: str) -> RequestSpec:
        if key not in self._specs:
            self._specs[key] = build_request_spec(
                base_url=problems_api_path.set_base_url(),
                base_path=base_path,
                headers=get_problems_headers(),
            )
        return self._specs[key]

    def setup_all_specs(self) -> None:
        """Builds every spec up front, mirroring `specBuilder.setupAllSpecs()`."""
        for key, base_path in (
            ("problem_list", problems_api_path.PROBLEM_LIST),
            ("problem_list_get", problems_api_path.PROBLEM_LIST_GET),
            ("problem_detail", problems_api_path.PROBLEM_DETAIL),
            ("problem_lock", problems_api_path.PROBLEM_LOCK),
            ("problem_unlock", problems_api_path.PROBLEM_UNLOCK),
            ("problem_clone", problems_api_path.PROBLEM_CLONE),
            ("problem_testcase_list", problems_api_path.PROBLEM_TESTCASE_LIST),
            ("problem_testcase_detail", problems_api_path.PROBLEM_TESTCASE_DETAIL),
            ("problem_submission_list", problems_api_path.PROBLEM_SUBMISSION_LIST),
            ("problem_submission_by_user", problems_api_path.PROBLEM_SUBMISSION_BY_USER),
            ("learn_feed_item", problems_api_path.LEARN_FEED_ITEM),
            ("submission_list", problems_api_path.SUBMISSION_LIST),
            ("submission_detail", problems_api_path.SUBMISSION_DETAIL),
            ("submission_revisions", problems_api_path.SUBMISSION_REVISIONS),
            ("submission_code_repo", problems_api_path.SUBMISSION_CODE_REPO),
            ("submission_submit", problems_api_path.SUBMISSION_SUBMIT),
        ):
            self._spec_for(key, base_path)

    def get_spec(self, key: str) -> RequestSpec:
        return self._specs.get(key) or self._spec_for(key, getattr(problems_api_path, key.upper()))
