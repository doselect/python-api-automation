"""
Ports the header-building side of tests/regression_api_methods/contest/*.py
(do-api-automation): every one of the 36 source functions builds its headers with a bare
`generate_headers(USER_TYPE_RECRUITER, "default", shared_data)` call — none of them `.update()`
any endpoint-specific overrides (unlike ai_interview/content_creator) — so every spec below uses
`default_recruiter_headers(auth_manager)` unmodified. Confirmed by reading every one of the 36
source files directly rather than assuming from utils/header_generator.py's `case "default"`
branch alone.
"""
from __future__ import annotations

from src.constants.paths import contest_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.specs.session_auth_headers import default_recruiter_headers


class ContestSpecBuilder:
    """Builds the reusable request specs for the ported `contest` regression endpoints."""

    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager

    def _headers(self) -> dict[str, str]:
        return default_recruiter_headers(self._auth_manager)

    def contest_list_spec(self) -> RequestSpec:
        """Mirrors post_create_contest.py/post_create_team_contest.py/post_create_2phase_*.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.CONTEST_LIST,
            headers=self._headers(),
        )

    def contest_detail_spec(self) -> RequestSpec:
        """Mirrors get_contest_details.py/get_phase_details.py/most patch_*.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.CONTEST_DETAIL,
            headers=self._headers(),
        )

    def contest_phase_list_spec(self) -> RequestSpec:
        """Mirrors convert_1phase_to_2phase_contest.py's new-phase POST headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.CONTEST_PHASE_LIST,
            headers=self._headers(),
        )

    def contest_phase_detail_spec(self) -> RequestSpec:
        """Mirrors convert_2phase_to_1phase_contest.py's phase-DELETE + patch_add_criteria.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.CONTEST_PHASE_DETAIL,
            headers=self._headers(),
        )

    def contest_clone_spec(self) -> RequestSpec:
        """Mirrors post_clone_contest.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.CONTEST_CLONE,
            headers=self._headers(),
        )

    def all_contests_spec(self) -> RequestSpec:
        """Mirrors get_all_contest.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.ALL_CONTESTS,
            headers=self._headers(),
        )

    def latest_contest_spec(self) -> RequestSpec:
        """Mirrors get_latest_contest.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.LATEST_CONTEST,
            headers=self._headers(),
        )

    def problems_modify_spec(self) -> RequestSpec:
        """Mirrors post_add_problem.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.PROBLEMS_MODIFY,
            headers=self._headers(),
        )

    def test_section_spec(self) -> RequestSpec:
        """Mirrors post_add_remove_problem_section.py's headers."""
        return build_request_spec(
            base_url=contest_api_path.set_base_url(), base_path=contest_api_path.TEST_SECTION,
            headers=self._headers(),
        )
