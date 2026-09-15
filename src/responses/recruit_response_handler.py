"""
Ports tests/regression_api_methods/recruit/*.py (do-api-automation): one method per source
function, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (same rationale as doiq_response_handler.py's docstring).

Started as a minimal 5-method slice (post_create_test/get_test_details/get_list_of_problems/
post_add_problem/get_problem_details) added by the `hacker`-porting agent for its attempt-flow
prerequisite calls; extended here to cover the rest of the domain.

`shared_data` threading is replaced with explicit return values/parameters throughout, matching the
ai_interview/contest precedent. Two source quirks are preserved verbatim rather than "fixed" (both
documented on their methods below, mirroring how contest_response_handler.py's module docstring
documents its own preserved-quirks): `get_solutionset`/`get_proctor_verdict` hardcode
`PROCTORING_TEST_SLUG`/`CANDIDATE_USERNAME_FOR_SOLUTIONSET`/`SOLUTIONSET_ID`, ignoring whatever
test/candidate a caller's flow actually produced; `post_send_reminder`'s URL and query-param
`test_slug` fall back to two different literals ("60y65" vs `TEST_SLUG_RECRUIT`) when none is
supplied, exactly as the source's two independently-resolved `shared_data.get(...)` calls do.

`patch_test_details` deliberately does not assert internally (unlike the source's own
`assert response.status_code in [202]`) — it just returns the status code, mirroring how
contest_response_handler.py's `_patch_contest` (non-asserting) vs `_patch_contest_with_retry`
(asserting) already coexist in this framework. The source's own call sites need this either way:
test_assessment_updates.py wants the plain assert to hold; test_assessment_lock_unlock.py wants to
*inspect* the status after an expected failure (wrapping the call in `try/except AssertionError:
pass` and then asserting on `shared_data["last_status_code"]`, since the source's `except` branch
sets that before re-raising) — returning the status either way lets both ported tests assert
directly on `result["status_code"]` without needing exception-carried state.
"""
from __future__ import annotations

from typing import Any, Optional

import requests

from src.core.do_api_config import (
    CANDIDATE_USERNAME,
    CANDIDATE_USERNAME_FOR_SOLUTIONSET,
    CONTEST_ID,
    DOSELECT_COMPANY_SLUG,
    PROCTORING_TEST_SLUG,
    RECRUITER_EMAIL,
    RECRUITER_ID,
    RECRUITER_USERNAME,
    SOLUTIONSET_ID,
    TEST_SLUG_RECRUIT,
)
from src.core.do_api_helpers import retry_api_call
from src.core.rest_client import execute_request
from src.constants.paths import recruit_api_path
from src.helpers.recruit.payloads import (
    PATCH_TEST_DETAILS_PAYLOAD,
    add_problem_payload,
    add_section_payload,
    create_invite_payload,
    create_lock_payload,
    create_test_payload,
    delete_invite_payload,
    delete_section_payload,
    get_increase_test_duration_payload,
    patch_company_payload,
    patch_solution_review_payload,
    post_add_max_retakes_payload,
    post_clear_bulk_reminder_payload,
    post_clone_test_payload,
    post_direct_pdf_payload,
    post_remove_retakes_payload,
    post_reset_test_solutionset_payload,
    send_reminder_payload,
)
from src.specs.recruit_spec_builder import RecruitSpecBuilder

_HACKATHON_UUID = "1744108799898"


class RecruitResponseHandler:
    """Wraps a RecruitSpecBuilder to centralize the ported `recruit` regression API calls."""

    def __init__(self, spec_builder: RecruitSpecBuilder) -> None:
        self._spec_builder = spec_builder

    # -------------------------------------------------------------------------------------
    # minimal slice (hacker attempt-flow prerequisite) — unchanged from the initial port
    # -------------------------------------------------------------------------------------

    def post_create_test(self, test_type: str = "RECRUIT", duration: int = 120) -> dict[str, Any]:
        """Mirrors post_create_test.py::post_create_test(shared_data, test_type, duration)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = create_test_payload(test_type, duration)
        response = execute_request(
            self._spec_builder.create_test_spec(), "POST", query_params=params, body=payload,
            expected_status_code=201,
        )
        response_data = response.json()
        return {
            "status_code": response.status_code,
            "test_slug": response_data.get("slug"),
            "test_id": response_data.get("id"),
        }

    def get_test_details(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors tests/regression_api_methods/common/get_test_details.py's "recruiter" branch."""
        resolved_slug = test_slug or "89a8n"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "is_test_env": "false"}
        response = execute_request(
            self._spec_builder.test_details_spec(), "GET", path_params={"testSlug": resolved_slug},
            query_params=params, expected_status_code=200,
        )
        response_data = response.json()
        return {
            "status_code": response.status_code,
            "test_id": response_data.get("id"),
            "sections": response_data.get("sections") or [],
        }

    def get_list_of_problems(
        self, test_slug: str, category: str, problem_type: str, num_of_problems: int, limit: str = "10"
    ) -> dict[str, Any]:
        """Mirrors get_list_of_problems.py::get_list_of_problems(shared_data, category, problem_type, num_of_problems, limit)."""
        params = {
            "index": "problem",
            "limit": limit,
            "narrow": (
                f"category|{category}||is_active|true||archived|false||problem_type|{problem_type}"
                "||visible_marketplace|true||||"
            ),
            "offset": "0",
            "order_by": "-modified",
            "page_type": "library",
            "q": "",
            "tag": "",
            "view": "",
        }
        response = execute_request(
            self._spec_builder.search_problems_spec(test_slug), "GET", query_params=params,
        )
        if response.status_code not in (200, 304):
            raise AssertionError(f"Expected status code 200/304, got {response.status_code}")
        resp_data = response.json()
        prob_to_add = [resp_data["objects"][0]["objects"][i]["slug"] for i in range(num_of_problems)]
        return {"status_code": response.status_code, "prob_to_add": prob_to_add}

    def post_add_problem(self, test_slug: str, section_slug: str, prob_to_add: list[str]) -> dict[str, Any]:
        """
        Mirrors post_add_problem.py::post_add_problem(shared_data): loops over `prob_to_add`,
        POSTing one at a time — only the *last* iteration's response is asserted/returned, matching
        the source (the loop variable is overwritten each pass, not accumulated).
        """
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response: Optional[requests.Response] = None
        for problem_slug in prob_to_add:
            payload = add_problem_payload(problem_slug, section_slug, test_slug)
            response = execute_request(
                self._spec_builder.add_problem_spec(test_slug), "POST", query_params=params, body=payload,
            )
        if response is None:
            raise AssertionError("prob_to_add was empty — nothing to add")
        if response.status_code != 202:
            raise AssertionError(f"Expected status code 202, got {response.status_code}")
        response_data = response.json()
        return {"status_code": response.status_code, "problem_id": response_data.get("problem_id")}

    def get_problem_details(self, problem_slug: str) -> dict[str, Any]:
        """Mirrors get_problem_details.py::get_problem_details(shared_data)."""
        # Source reuses generate_params(USER_TYPE_RECRUITER, "post_create_test", shared_data) here
        # (i.e. get_create_test_params) — same literal value, preserved as-is.
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.problem_details_spec(), "GET", path_params={"problemSlug": problem_slug},
            query_params=params, expected_status_code=200,
        )
        response_data = response.json()
        result: dict[str, Any] = {"status_code": response.status_code, "problem_type": response_data.get("problem_type")}
        if response_data.get("problem_type") in ("MCQ", "FIB"):
            correct_answer = response_data.get("mcq_options_correct") or []
            result["correct_answer"] = [item for sublist in correct_answer for item in sublist]
        elif response_data.get("problem_type") in ("SCR", "DBA"):
            solution_data = response_data.get("sample_solutions") or {}
            solution_lang, solution_code = next(iter(solution_data.items()))
            result["solution_lang"] = solution_lang
            result["solution_code"] = solution_code
        return result

    # -------------------------------------------------------------------------------------
    # company / recruiter / team
    # -------------------------------------------------------------------------------------

    def get_company_details(self, company_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_company_details.py::get_company_details(shared_data)."""
        resolved_slug = company_slug or DOSELECT_COMPANY_SLUG
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.company_detail_spec(), "GET", path_params={"companySlug": resolved_slug},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code, "company_details": response.json()}

    def patch_company_details(self, company_details: dict, company_slug: Optional[str] = None) -> dict[str, Any]:
        """
        Mirrors patch_company_details.py::patch_company_details(shared_data). Takes the prior
        get_company_details() call's `company_details` body directly (source read it back off
        `shared_data["company_details"]`, a stashed GET response).
        """
        resolved_slug = company_slug or "doselect_performance_testing"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = patch_company_payload(company_details)
        response = execute_request(
            self._spec_builder.patch_company_spec(), "PATCH", path_params={"companySlug": resolved_slug},
            query_params=params, body=payload, expected_status_code=202,
        )
        return {"status_code": response.status_code}

    def get_company_feeds(self) -> dict[str, Any]:
        """Mirrors get_company_feeds.py::get_company_feeds(auth_manager, shared_data)."""
        response = execute_request(
            self._spec_builder.company_feeds_spec(), "GET", query_params={"limit": 15},
        )
        if response.status_code not in (200, 304):
            raise AssertionError(f"Expected status code 200/304, got {response.status_code}")
        return {"status_code": response.status_code}

    def get_company_interactions(self, interaction_email: Optional[str] = None, company_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_company_interactions.py::get_company_interactions(auth_manager, shared_data)."""
        resolved_email = interaction_email or RECRUITER_EMAIL
        resolved_slug = company_slug or DOSELECT_COMPANY_SLUG
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.company_interactions_spec(resolved_email), "GET",
            path_params={"companySlug": resolved_slug, "email": resolved_email},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_company_recruiters(self, company_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_company_recruiters.py::get_company_recruiters(shared_data)."""
        resolved_slug = company_slug or "doselect_performance_testing"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.company_recruiters_spec(), "GET", path_params={"companySlug": resolved_slug},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_company_team_invites(self, company_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_company_team_invites.py::get_company_team_invites(shared_data)."""
        resolved_slug = company_slug or DOSELECT_COMPANY_SLUG
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.company_team_invites_spec(), "GET", path_params={"companySlug": resolved_slug},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_team_member_stats(self) -> dict[str, Any]:
        """Mirrors get_team_member_stats.py::get_team_member_stats(shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.team_member_stats_spec(), "GET", query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_team_monthly_stats(self) -> dict[str, Any]:
        """Mirrors get_team_monthly_stats.py::get_team_monthly_stats(auth_manager, shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.team_monthly_stats_spec(), "GET", query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_team_quotas(self) -> dict[str, Any]:
        """Mirrors get_team_quotas.py::get_team_quotas(auth_manager, shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.team_quotas_spec(), "GET", query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_recruiter_details(self) -> dict[str, Any]:
        """Mirrors get_recruiter_details.py::get_recruiter_details(auth_manager, shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_EMAIL}
        response = execute_request(
            self._spec_builder.recruiter_detail_spec(), "GET", path_params={"recruiterId": RECRUITER_ID},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_create_invite(
        self, candidate_email: Optional[str], invite_type: str = "candidate", test_slug: Optional[str] = None
    ) -> dict[str, Any]:
        """Mirrors post_create_invite.py::post_create_invite(auth_manager, shared_data, candidate_email, type)."""
        payload = create_invite_payload(test_slug or TEST_SLUG_RECRUIT, invite_type)
        if candidate_email:
            payload["email_list"][0]["email"] = candidate_email
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        spec = (
            self._spec_builder.create_candidate_invite_spec(test_slug)
            if invite_type == "candidate"
            else self._spec_builder.create_team_invite_spec()
        )
        response = execute_request(spec, "POST", query_params=params, body=payload, expected_status_code=200)
        return {"status_code": response.status_code}

    def delete_invite(self, invite_id) -> dict[str, Any]:
        """Mirrors delete_invite.py::delete_invite(auth_manager, shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = delete_invite_payload(invite_id)
        response = execute_request(
            self._spec_builder.delete_invite_spec(), "DELETE", path_params={"inviteId": invite_id},
            query_params=params, body=payload, expected_status_code=204,
        )
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # hackathon / generic library / user
    # -------------------------------------------------------------------------------------

    def get_hackathon_company(self, company_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_hackathon_company.py::get_hackathon_company(auth_manager, shared_data)."""
        resolved_slug = company_slug or DOSELECT_COMPANY_SLUG
        response = execute_request(
            self._spec_builder.hackathon_company_spec(), "GET", path_params={"companySlug": resolved_slug},
            query_params={"uuId": _HACKATHON_UUID}, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_hackathon_contests(self) -> dict[str, Any]:
        """Mirrors get_hackathon_contests.py::get_hackathon_contests(auth_manager, shared_data)."""
        params = {"page": 1, "limit": 10, "uuId": _HACKATHON_UUID}
        response = execute_request(
            self._spec_builder.hackathon_contests_spec(), "GET", query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_hackathon_contest_details(self, contest_id: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_hackathon_contest_details.py::get_hackathon_contest_details(auth_manager, shared_data)."""
        resolved_id = contest_id or CONTEST_ID
        response = execute_request(
            self._spec_builder.hackathon_contest_details_spec(resolved_id), "GET",
            path_params={"contestId": resolved_id}, query_params={"uuId": _HACKATHON_UUID}, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_hackathon_participant_view(self, contest_id: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_hackathon_participant_view.py::get_hackathon_participant_view(shared_data)."""
        resolved_id = contest_id or CONTEST_ID
        params = {"contestId": resolved_id, "offset": 0, "limit": 10, "uuId": _HACKATHON_UUID}
        response = execute_request(
            self._spec_builder.hackathon_participant_view_spec(resolved_id), "GET", query_params=params,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_hackathon_participant_count_user_state(self, contest_id: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_hackathon_participant_count_user_state.py::get_hackathon_participant_count_user_state(shared_data)."""
        resolved_id = contest_id or CONTEST_ID
        params = {"contestId": resolved_id, "uuId": _HACKATHON_UUID}
        response = execute_request(
            self._spec_builder.hackathon_participant_count_user_state_spec(resolved_id), "GET", query_params=params,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_hackathon_quotas(self) -> dict[str, Any]:
        """Mirrors get_hackathon_quotas.py::get_hackathon_quotas(auth_manager, shared_data)."""
        response = execute_request(
            self._spec_builder.hackathon_quotas_spec(), "GET", query_params={"uuId": _HACKATHON_UUID},
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    @staticmethod
    def _generic_library_narrow(narrow_filters: Optional[dict[str, str]] = None) -> str:
        """Mirrors get_generic_library_params's narrow-string builder (default filters: category=MAR,
        archived=false, visible_marketplace=true, is_active=true — in that literal order)."""
        filters = narrow_filters or {
            "category": "MAR", "archived": "false", "visible_marketplace": "true", "is_active": "true",
        }
        return "||".join(f"{key}|{value}" for key, value in filters.items()) + "||"

    def get_generic_library(
        self, contest_id: str = "3007", phase_id: str = "3165",
        section_id: str = "a72a6d67f4cd466ab99b2725e95b70eb",
    ) -> dict[str, Any]:
        """Mirrors get_generic_library.py::get_generic_library(auth_manager, shared_data)."""
        params = {
            "index": "problem", "visibility": "public", "limit": 10, "offset": 0, "order_by": "-modified",
            "tag": "", "q": "", "narrow": self._generic_library_narrow(), "uuId": _HACKATHON_UUID,
        }
        response = execute_request(
            self._spec_builder.generic_library_spec(contest_id, phase_id, section_id), "GET", query_params=params,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_user_details(self, username: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_user_details.py::get_user_details(auth_manager, shared_data)."""
        resolved_username = username or RECRUITER_USERNAME
        response = execute_request(
            self._spec_builder.user_details_spec(), "GET", path_params={"username": resolved_username},
            query_params={"uuId": _HACKATHON_UUID}, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_user_permissions(self) -> dict[str, Any]:
        """Mirrors get_user_permissions.py::get_user_permissions(auth_manager, shared_data)."""
        response = execute_request(
            self._spec_builder.user_permissions_spec(), "GET", query_params={"uuId": _HACKATHON_UUID},
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # candidates / solutions / proctoring / reports
    # -------------------------------------------------------------------------------------

    def get_crunch_hacker_data(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_crunch_hacker_data.py (dispatcher: generate_headers("recruit","get_crunch_hacker_data",...))."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "username": CANDIDATE_USERNAME}
        response = execute_request(
            self._spec_builder.crunch_hacker_data_spec(test_slug), "GET", query_params=params,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_test_report_comment(self, test_slug: Optional[str] = None, candidate_username: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_test_report_comment.py (dispatcher: "get_test_report_comment")."""
        params = {
            "__env": "PLT", "__user": RECRUITER_USERNAME,
            "hacker__username": candidate_username or CANDIDATE_USERNAME_FOR_SOLUTIONSET,
            "test__slug": test_slug or PROCTORING_TEST_SLUG,
        }
        response = execute_request(
            self._spec_builder.test_report_comment_spec(test_slug), "GET", query_params=params,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_problem_search(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_problem_search.py::get_problem_search(auth_manager, shared_data)."""
        params = {
            "index": "problem", "limit": 10,
            "narrow": "category|MAR||is_active|true||archived|false||visible_marketplace|true||||",
            "offset": 0, "order_by": "-modified", "page_type": "library", "q": "", "tag": "", "view": "",
        }
        response = execute_request(
            self._spec_builder.problem_search_spec(test_slug), "GET", query_params=params,
        )
        if response.status_code not in (200, 304):
            raise AssertionError(f"Expected status code 200/304, got {response.status_code}")
        return {"status_code": response.status_code}

    def get_search_results(self) -> dict[str, Any]:
        """Mirrors get_search_results.py::get_search_results(auth_manager, shared_data)."""
        params = {
            "index": "test", "limit": 3, "narrow": "archived|false||test_type|GEN||mode|TIM",
            "offset": 0, "page_type": "", "tag": "", "view": "",
        }
        response = execute_request(
            self._spec_builder.search_results_spec(), "GET", query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_solution(
        self, test_slug: Optional[str] = None, candidate_username: Optional[str] = None,
        problem_slug: Optional[str] = None, solution_slug: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors get_solution.py (dispatcher: "get_solution") — preserves the source's own
        retry-then-assert loop via `retry_api_call`."""
        resolved_slug = solution_slug or "qg339xvl"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "source": ""}
        spec = self._spec_builder.solution_spec(test_slug, candidate_username, problem_slug)
        url = recruit_api_path.set_base_url() + recruit_api_path.SOLUTION_DETAIL.format(solutionSlug=resolved_slug)
        response = execute_request(spec, "GET", path_params={"solutionSlug": resolved_slug}, query_params=params)
        retry = 1
        while response.status_code != 200 and retry < 4:
            response = retry_api_call(url=url, headers=spec.headers, params=params, method="get", max_retries=4, retry=retry)
            retry += 1
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200, got {response.status_code}")
        return {"status_code": response.status_code}

    def get_solution_revisions(
        self, test_slug: Optional[str] = None, candidate_username: Optional[str] = None,
        problem_slug: Optional[str] = None, solution_slug: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors get_solution_revisions.py::get_solution_revisions(auth_manager, shared_data)."""
        resolved_slug = solution_slug or "qg339xvl"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.solution_revisions_spec(test_slug, candidate_username, problem_slug), "GET",
            path_params={"solutionSlug": resolved_slug}, query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def patch_solution_review(
        self, test_slug: Optional[str] = None, candidate_username: Optional[str] = None,
        problem_slug: Optional[str] = None, solution_slug: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors patch_solution_review.py::patch_solution_review(auth_manager, shared_data)."""
        resolved_slug = solution_slug or "qg339xvl"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = patch_solution_review_payload("ACC", 19)
        response = execute_request(
            self._spec_builder.solution_review_spec(test_slug, candidate_username, problem_slug), "PATCH",
            path_params={"solutionSlug": resolved_slug}, query_params=params, body=payload,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_direct_pdf(
        self, solutionset_id, test_slug: Optional[str] = None, candidate_username: Optional[str] = None,
        problem_slug: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Mirrors post_direct_pdf.py::post_direct_pdf(auth_manager, shared_data). `solutionset_id`
        is required (no default) — the source does `shared_data["solutionset_id"]` with no
        fallback, i.e. a hard `KeyError` if absent; a required positional arg is the equivalent
        "must supply this" contract here.
        """
        resolved_test_slug = test_slug or TEST_SLUG_RECRUIT
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = post_direct_pdf_payload(resolved_test_slug, [solutionset_id])
        response = execute_request(
            self._spec_builder.direct_pdf_spec(test_slug, candidate_username, problem_slug), "POST",
            query_params=params, body=payload, expected_status_code=201,
        )
        return {"status_code": response.status_code}

    def get_direct_pdf_status(
        self, test_slug: Optional[str] = None, candidate_username: Optional[str] = None,
        problem_slug: Optional[str] = None,
    ) -> dict[str, Any]:
        """Mirrors get_direct_pdf_status.py::get_direct_pdf_status(auth_manager, shared_data)."""
        resolved_test_slug = test_slug or TEST_SLUG_RECRUIT
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.direct_pdf_status_spec(test_slug, candidate_username, problem_slug), "GET",
            path_params={"testSlug": resolved_test_slug}, query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_solutionset(self) -> dict[str, Any]:
        """
        Mirrors get_solutionset.py::get_solutionset(auth_manager, shared_data). The source
        hardcodes `PROCTORING_TEST_SLUG`/`CANDIDATE_USERNAME_FOR_SOLUTIONSET` for both the URL and
        the query params — it never reads `shared_data.get("test_slug"/"candidate_username")` at
        all, so this call is unaffected by whatever test/candidate a preceding flow produced.
        Preserved as-is (see module docstring); also note the source's `test_extend_test_time.py`
        calls this inside a retry loop as `get_solutionset(shared_data)` (one positional arg) after
        first calling it correctly as `get_solutionset(auth_manager, shared_data)` — a latent
        `TypeError` in the source since the function requires both params. Moot here: this method
        takes no live-flow args at all, so the ported test's retry loop just calls
        `recruit_response_handler.get_solutionset()` uniformly both times.
        """
        params = {
            "__env": "PLT", "__user": RECRUITER_USERNAME, "contest_id": "", "test_slug": PROCTORING_TEST_SLUG,
            "username": CANDIDATE_USERNAME_FOR_SOLUTIONSET,
        }
        response = execute_request(
            self._spec_builder.solutionset_spec(), "GET", path_params={"testSlug": PROCTORING_TEST_SLUG},
            query_params=params, expected_status_code=200,
        )
        response_data = response.json()
        return {"status_code": response.status_code, "solutionset_status": response_data.get("status")}

    def get_proctor_verdict(self) -> dict[str, Any]:
        """
        Mirrors get_proctor_verdict.py::get_proctor_verdict(auth_manager, shared_data) — uses
        `SOLUTIONSET_ID`/`PROCTORING_TEST_SLUG` constants unconditionally, same as `get_solutionset`
        above (see that method's docstring).
        """
        params = {
            "page": "1", "mode": "batch", "test_slug": PROCTORING_TEST_SLUG, "contest_id": "",
            "__env": "PLT", "__user": RECRUITER_USERNAME,
        }
        response = execute_request(
            self._spec_builder.proctor_verdict_spec(), "GET", path_params={"solutionsetId": SOLUTIONSET_ID},
            query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def get_test_candidates(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_test_candidates.py::get_test_candidates(auth_manager, shared_data) — preserves
        the source's own retry-while-empty loop via `retry_api_call`."""
        resolved_slug = test_slug or "89a8n"
        params = {"_limit": 15, "_offset": 0, "_sort": "-total_score,time_taken", "aggs": "status", "q": ""}
        spec = self._spec_builder.test_candidates_spec(resolved_slug)
        url = recruit_api_path.set_dolores_base_url() + recruit_api_path.TEST_CANDIDATES.format(testSlug=resolved_slug)
        response = execute_request(spec, "GET", path_params={"testSlug": resolved_slug}, query_params=params)
        retry = 1
        while response.status_code == 200 and len(response.json().get("objects") or []) == 0 and retry < 4:
            response = retry_api_call(url=url, headers=spec.headers, params=params, method="get", max_retries=4, retry=retry)
            retry += 1
        response_data = response.json()
        invite_id = response_data.get("objects")[0].get("invite").get("id")
        if response.status_code != 200:
            raise AssertionError(f"Expected status code 200, got {response.status_code}")
        return {"status_code": response.status_code, "invite_id": invite_id}

    # -------------------------------------------------------------------------------------
    # test lifecycle: lock / try-as-recruiter / clone / sections / patch
    # -------------------------------------------------------------------------------------

    def post_create_remove_lock(self, test_slug: str, lock_action: str) -> dict[str, Any]:
        """Mirrors post_create_lock.py::post_create_remove_lock(auth_manager, shared_data) — `lock_action` is "create"/"remove"."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = create_lock_payload(test_slug)
        response = execute_request(
            self._spec_builder.create_lock_spec(test_slug), "POST", path_params={"lockAction": lock_action},
            query_params=params, body=payload, expected_status_code=204,
        )
        return {"status_code": response.status_code}

    def patch_test_details(self, test_slug: str) -> dict[str, Any]:
        """Mirrors patch_test_details.py::patch_test_details(auth_manager, shared_data) — see module
        docstring for why this doesn't assert internally."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.patch_test_details_spec(test_slug), "PATCH", path_params={"testSlug": test_slug},
            query_params=params, body=PATCH_TEST_DETAILS_PAYLOAD,
        )
        return {"status_code": response.status_code}

    def post_try_test_as_recruiter(self, test_slug: str) -> dict[str, Any]:
        """Mirrors post_try_test_as_recruiter.py::post_try_test_as_recruiter(auth_manager, shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "slug": test_slug}
        response = execute_request(
            self._spec_builder.try_test_as_recruiter_spec(test_slug), "POST", query_params=params, body={},
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_add_remove_section(
        self, test_slug: Optional[str], action: str = "add", section_slug: Optional[str] = None
    ) -> dict[str, Any]:
        """Mirrors post_add_section.py::post_add_remove_section(shared_data, action, section_slug)."""
        resolved_slug = test_slug or "89a8n"
        payload = add_section_payload() if action == "add" else delete_section_payload()
        if section_slug:
            payload["section_slug"] = section_slug
        payload["test_slug"] = resolved_slug
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "test_slug": resolved_slug}
        response = execute_request(
            self._spec_builder.post_add_section_spec(test_slug), "POST", query_params=params, body=payload,
            expected_status_code=202,
        )
        return {"status_code": response.status_code}

    def post_clone_test(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors post_clone_test.py::post_clone_test(shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "test_slug": test_slug or TEST_SLUG_RECRUIT}
        response = execute_request(
            self._spec_builder.clone_test_spec(), "POST", query_params=params, body=post_clone_test_payload(),
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # retakes / duration / solutionset reset / reminders
    # -------------------------------------------------------------------------------------

    def post_add_max_retakes(self, invite_id, retake_count: int = 2) -> dict[str, Any]:
        """Mirrors post_add_max_retakes.py::post_add_max_retakes(shared_data, retake_count)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = post_add_max_retakes_payload(invite_id, retake_count)
        response = execute_request(
            self._spec_builder.add_max_retakes_spec(), "POST", query_params=params, body=payload,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_remove_retakes(self, invite_id, test_slug: Optional[str] = None, retake_count: int = 1) -> dict[str, Any]:
        """Mirrors post_remove_retakes.py::post_remove_retakes(shared_data, retake_count)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = post_remove_retakes_payload(invite_id, retake_count)
        response = execute_request(
            self._spec_builder.remove_retakes_spec(test_slug), "POST", query_params=params, body=payload,
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_increase_test_duration(self, sections: list, invite_id, test_slug: Optional[str] = None, duration: int = 5) -> dict[str, Any]:
        """Mirrors post_increase_test_duration.py::post_increase_test_duration(shared_data) — the
        source's call site always passes `duration=5`."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        payload = get_increase_test_duration_payload(sections, invite_id, duration)
        response = execute_request(
            self._spec_builder.increase_test_duration_spec(test_slug), "POST", query_params=params, body=payload,
            expected_status_code=202,
        )
        return {"status_code": response.status_code}

    def post_reset_test_solutionset(self, invite_id, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors post_reset_test_solutionset.py::post_reset_test_solutionset(shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.reset_test_solutionset_spec(test_slug), "POST",
            path_params={"inviteId": invite_id}, query_params=params, body=post_reset_test_solutionset_payload(),
            expected_status_code=202,
        )
        return {"status_code": response.status_code}

    def get_bulk_reminder_status(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors get_bulk_reminder_status.py::get_bulk_reminder_status(shared_data)."""
        params = {"action": "reminder", "__env": "PLT", "__user": RECRUITER_USERNAME}
        response = execute_request(
            self._spec_builder.bulk_reminder_status_spec(test_slug), "GET",
            path_params={"reminderId": RECRUITER_ID}, query_params=params, expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_clear_bulk_reminder(self, test_slug: Optional[str] = None) -> dict[str, Any]:
        """Mirrors post_clear_bulk_reminder.py::post_clear_bulk_reminder(shared_data)."""
        params = {
            "action": "reminder", "testSlug": test_slug or TEST_SLUG_RECRUIT, "__env": "PLT",
            "__user": RECRUITER_USERNAME,
        }
        response = execute_request(
            self._spec_builder.clear_bulk_reminder_spec(test_slug), "POST",
            path_params={"reminderId": RECRUITER_ID}, query_params=params, body=post_clear_bulk_reminder_payload(),
            expected_status_code=200,
        )
        return {"status_code": response.status_code}

    def post_send_reminder(self, invite_id, test_slug: Optional[str] = None) -> dict[str, Any]:
        """
        Mirrors post_send_reminder.py::post_send_reminder(shared_data, test_slug). The source
        resolves the URL's test_slug (`shared_data.get("test_slug", "60y65")`) and the query
        param's test_slug (`get_send_reminder_params` -> `shared_data.get("test_slug", TEST_SLUG_RECRUIT)`)
        independently, with two *different* literal fallbacks — preserved as-is; they only diverge
        when `test_slug` is left unset.
        """
        url_test_slug = test_slug or "60y65"
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME, "test_slug": test_slug or TEST_SLUG_RECRUIT}
        payload = send_reminder_payload(invite_id)
        response = execute_request(
            self._spec_builder.send_reminder_spec(test_slug), "POST", path_params={"testSlug": url_test_slug},
            query_params=params, body=payload, expected_status_code=200,
        )
        return {"status_code": response.status_code}
