"""
Ports tests/regression_api_methods/interview/*.py (42 files, do-api-automation): one method per
source function, executed through src.core.rest_client.execute_request instead of raw `requests`
calls + manual try/except/finally logging (see doiq_response_handler.py's docstring — same
rationale). `shared_data` threading is replaced by explicit parameters/return values throughout
(e.g. `get_latest_job_role_slug`/`get_interview_meta`/`generate_fresh_interview_token` return the
slug/token directly instead of stashing it in shared_data) — callers (tests, or other methods on
this class) pass those values along explicitly, mirroring how ai_interview_response_handler.py
threads data between its own chained calls.

Cross-file call chains from the source are preserved as one method calling another (not
duplicated): get_latest_job_role_slug is reused by delete_recommended_problem/get_ad_hoc_role/
get_job_role_details/post_archieve_job_role/post_clone_job_role/post_create_evaluation_criteria/
generate_fresh_interview_token/post_recommend_problem/post_schedule_interview/
search_interviews_based_on_status, exactly as in the source.
"""
from __future__ import annotations

import time
from typing import Any, Optional

import requests

from src.core.do_api_config import CANDIDATE_EMAIL_INTERVIEW, RECRUITER_EMAIL, RECRUITER_USERNAME
from src.core.do_api_helpers import generate_fake_name, generate_random_email
from src.core.rest_client import execute_request
from src.helpers.interview.email_otp import get_otp_from_email_helper
from src.helpers.interview.payloads import (
    add_interviewer_payload,
    ask_feedback_payload,
    create_evaluation_criteria_payload,
    create_job_role_payload,
    create_join_interview_payload,
    create_recommend_problem_payload,
    create_schedule_interview_payload,
    delete_interviewer_payload,
    final_status_payload,
    interviewer_feedback_payload,
    upcoming_interview_slug_payload,
)
from src.constants.paths import interview_api_path
from src.specs.interview_spec_builder import InterviewSpecBuilder


def _extract_interview_slugs(response_data: Any) -> list:
    """Mirrors get_ad_hoc_role.py::extract_interview_slugs(response_data)."""
    interview_slugs = []
    if isinstance(response_data, dict):
        if isinstance(response_data.get("data"), list):
            for item in response_data["data"]:
                if isinstance(item, dict) and "slug" in item:
                    interview_slugs.append(item["slug"])
        elif "slug" in response_data:
            interview_slugs.append(response_data["slug"])
    return interview_slugs


class InterviewResponseHandler:
    """Wraps an InterviewSpecBuilder to centralize the ported `interview` regression API calls."""

    def __init__(self, spec_builder: InterviewSpecBuilder) -> None:
        self._spec_builder = spec_builder

    # ------------------------------------------------------------------ job roles

    def get_latest_job_role_slug(self) -> str:
        """
        Mirrors get_latest_job_role_slug.py::get_latest_job_role_slug(shared_data): returns the
        slug of the first search result, creating a new job role via post_create_new_jobrole()
        when none exist.
        """
        params = {"limit": 1, "offset": 0}  # mirrors get_latest_job_role_slug_params
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.SEARCH_ROLE), "GET", query_params=params,
            expected_status_code=200,
        )
        results = response.json().get("results", []) if response.text else []
        if results:
            slug = results[0].get("slug")
            if slug:
                return slug
        return self.post_create_new_jobrole()

    def post_create_new_jobrole(self) -> str:
        """Mirrors post_create_new_jobrole.py::post_create_new_jobrole(shared_data): returns the created slug."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_LIST), "POST", body=create_job_role_payload(),
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response.json().get("slug")

    def get_all_job_roles(self) -> requests.Response:
        """Mirrors get_all_job_roles.py::get_all_job_roles(shared_data)."""
        params = {"offset": 0, "limit": 10}  # mirrors get_offset_limit_params
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.SEARCH_ROLE), "GET", query_params=params,
            expected_status_code=200,
        )

    def get_ad_hoc_role(self) -> requests.Response:
        """Mirrors get_ad_hoc_role.py::get_ad_hoc_role(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_AD_HOC), "GET",
            path_params={"jobRoleSlug": job_role_slug}, expected_status_code=200,
        )

    def get_job_role_details(self) -> requests.Response:
        """Mirrors get_job_role_details.py::get_job_role_details(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_DETAIL), "GET",
            path_params={"jobRoleSlug": job_role_slug}, expected_status_code=200,
        )

    def post_archieve_job_role(self) -> requests.Response:
        """Mirrors post_archieve_job_role.py::post_archieve_job_role(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_ARCHIVE), "POST",
            path_params={"jobRoleSlug": job_role_slug},
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_clone_job_role(self) -> requests.Response:
        """Mirrors post_clone_job_role.py::post_clone_job_role(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_CLONE), "POST",
            path_params={"jobRoleSlug": job_role_slug},
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_create_evaluation_criteria(self) -> requests.Response:
        """Mirrors post_create_evaluation_criteria.py::post_create_evaluation_criteria(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_CRITERIA), "POST",
            path_params={"jobRoleSlug": job_role_slug}, body=create_evaluation_criteria_payload(),
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_recommend_problem(self) -> requests.Response:
        """
        Mirrors post_recommend_problem.py::post_recommend_problem(shared_data).

        The source sends `create_recommend_problem_payload()` — a literal `{}` — with no body at
        all; the server 400s that with "This field is required." for `name`/`slug`/`level`/
        `problem_type` (verified live against PLT). Populated here from a real search result, the
        same way `post_add_problem_during_interview` already sources a problem to attach.
        """
        job_role_slug = self.get_latest_job_role_slug()
        problems = self.get_search_problems().json().get("results", [])
        if not problems:
            raise AssertionError("get_search_problems returned no problems to recommend")
        problem = problems[0]
        payload = {
            "name": problem["name"],
            "slug": problem["slug"],
            "level": problem["level"],
            "problem_type": problem["problem_type"],
        }
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_RECOMMEND_PROBLEM), "POST",
            path_params={"jobRoleSlug": job_role_slug}, body=payload, expected_status_code=201,
        )

    def delete_recommended_problem(self, problem_slug: str = "m53ggx") -> requests.Response:
        """Mirrors delete_recommended_problem.py::delete_recommended_problem(shared_data, problem_slug)."""
        job_role_slug = self.get_latest_job_role_slug()
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_RECOMMEND_PROBLEM_DETAIL), "DELETE",
            path_params={"jobRoleSlug": job_role_slug, "problemSlug": problem_slug}, expected_status_code=200,
        )

    # ------------------------------------------------------------------ instant interviews / tokens

    def generate_fresh_interview_token(self) -> str:
        """Mirrors post_create_new_instant_link.py::generate_fresh_interview_token(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_AD_HOC), "POST",
            path_params={"jobRoleSlug": job_role_slug},
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        data = response.json()
        # Try different possible locations for the token (same fallback order as the source).
        token = (
            data.get("interview_token")
            or data.get("data", {}).get("interview_token")
            or data.get("token")
            or data.get("data", {}).get("access_code")
            or data.get("data", {}).get("slug")
            or data.get("slug")
        )
        if not token:
            raise AssertionError("No interview token found in response")
        return token

    def get_or_create_fresh_token(self, current_token: Optional[str] = None, force_refresh: bool = False) -> str:
        """Mirrors post_create_new_instant_link.py::get_or_create_fresh_token(shared_data, force_refresh)."""
        if not force_refresh and current_token:
            return current_token
        return self.generate_fresh_interview_token()

    def delete_instant_interview(self, interview_slug: str) -> requests.Response:
        """Mirrors delete_instant_interviews.py::delete_instant_interview(shared_data, interview_slug)."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_DETAIL), "DELETE",
            path_params={"interviewSlug": interview_slug},
        )
        assert response.status_code in (200, 204), f"Expected status code 200/204, got {response.status_code}"
        return response

    def delete_all_instant_interviews(self) -> dict:
        """Mirrors delete_instant_interviews.py::delete_all_instant_interviews(shared_data)."""
        get_response = self.get_ad_hoc_role()
        response_data = get_response.json() if get_response.text else {}
        interview_slugs = _extract_interview_slugs(response_data)

        if not interview_slugs:
            return {"success": True, "message": "No instant interviews found to delete", "deleted_count": 0}

        deleted_count = 0
        failed_count = 0
        errors: list = []
        for interview_slug in interview_slugs:
            try:
                self.delete_instant_interview(interview_slug)
                deleted_count += 1
            except AssertionError as e:
                failed_count += 1
                errors.append(f"Failed to delete interview {interview_slug}: {e}")

        if failed_count == 0:
            return {"success": True, "deleted_count": deleted_count, "failed_count": failed_count}
        return {"success": False, "deleted_count": deleted_count, "failed_count": failed_count, "errors": errors}

    # ------------------------------------------------------------------ interview lifecycle

    def get_interview_meta(self, interview_token: str) -> str:
        """Mirrors get_interview_meta.py::get_interview_meta(shared_data, interview_token): returns the slug."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_META), "GET",
            path_params={"interviewToken": interview_token}, expected_status_code=200,
        )
        return response.json()["slug"]

    def get_interview_invitation_status(self, interview_token: Optional[str] = None) -> requests.Response:
        """
        Mirrors get_interview_invitation_status.py::get_interview_invitation_status(shared_data,
        interview_token). Source falls back to `shared_data.get("current_interview_token")`, a key
        no call site ever sets, so it always falls through to `generate_fresh_interview_token`
        when `interview_token` isn't explicitly passed — preserved as-is.
        """
        if not interview_token:
            interview_token = self.generate_fresh_interview_token()
        interview_slug = self.get_interview_meta(interview_token)
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_INVITATION_STATUS), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_interview_questions(self, interview_slug: str) -> requests.Response:
        """Mirrors get_interview_questions.py::get_interview_questions(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_QUESTIONS), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_interview_report(self, interview_slug: str) -> requests.Response:
        """Mirrors get_interview_report.py::get_interview_report(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_REPORT), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_interview_status(self, interview_slug: str) -> requests.Response:
        """Mirrors get_interview_status.py::get_interview_status(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_STATUS), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_interview_technologies_list(self) -> requests.Response:
        """Mirrors get_interview_technologies_list.py::get_interview_technologies_list(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_TECHNOLOGY_LIST), "GET",
            expected_status_code=200,
        )

    def get_participants(self, interview_slug: str) -> requests.Response:
        """Mirrors get_participants.py::get_participants(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_PARTICIPANTS), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_recording_signed_url(self, interview_slug: str) -> requests.Response:
        """Mirrors get_recording_signed_url.py::get_recording_signed_url(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_RECORDING_SIGNED_URL), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def get_problem_setters(self) -> requests.Response:
        """Mirrors get_problem_setters.py::get_problem_setters(shared_data)."""
        params = {"__env": "PLT", "__user": RECRUITER_USERNAME}
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.COMPANY_PROBLEMSETTERS), "GET",
            query_params=params, expected_status_code=200,
        )

    def get_active_interviewers(self) -> requests.Response:
        """Mirrors get_active_interviewers.py::get_active_interviewers(shared_data) (DOLORES_BASE_URL host)."""
        params = {"is_active": "true", "_limit": 150, "_offset": 0}
        spec = self._spec_builder.default_spec(
            interview_api_path.SEARCH_INTERVIEWERS, base_url=interview_api_path.dolores_base_url()
        )
        return execute_request(spec, "GET", query_params=params, expected_status_code=200)

    def get_interview_gateway(self, gateway_token: str) -> requests.Response:
        """Mirrors get_interview_gateway.py::get_interview_gateway(shared_data, gateway_token)."""
        response = execute_request(self._spec_builder.interview_gateway_spec(gateway_token), "GET")
        assert response.status_code in (200, 302), f"Expected status code 200 or 302, got {response.status_code}"
        return response

    def search_interviews_based_on_status(self, status: str = "EXPIRED") -> requests.Response:
        """Mirrors get_search_interview_based_on_status.py::search_interviews_based_on_status(shared_data, status)."""
        job_role_slug = self.get_latest_job_role_slug()
        params = {"limit": 10, "offset": 0, "status": status, "job_role": job_role_slug}
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.SEARCH_INTERVIEW), "GET",
            query_params=params, expected_status_code=200,
        )

    def get_search_problems(self, search_term: str = "") -> requests.Response:
        """Mirrors get_search_problems.py::get_search_problems(shared_data, search_term)."""
        params: dict[str, Any] = {"limit": 10, "offset": 0, "problem_type": "SCR", "category": "PRI"}
        if search_term:
            params["search"] = search_term
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.SEARCH_PROBLEM), "GET", query_params=params,
            expected_status_code=200,
        )

    def post_add_problem_during_interview(
        self, first_problem_details: Optional[dict] = None, session_interview_token: Optional[str] = None,
    ) -> requests.Response:
        """
        Mirrors post_add_problem_during_interview.py::post_add_problem_during_interview(shared_data).
        `first_problem_details` replaces `shared_data.get("first_problem_details")` (populated in
        the source by a prior, separate `get_search_problems` call — same in the ported test).
        """
        params = {"limit": 10, "offset": 0, "problem_type": "SCR", "category": "PRI"}  # mirrors search_problems params
        session_interview_token = self.get_or_create_fresh_token(session_interview_token)
        interview_slug = self.get_interview_meta(session_interview_token)
        payload = create_recommend_problem_payload()
        if first_problem_details is not None:
            payload.update(
                {
                    "name": first_problem_details["name"],
                    "problem_slug": first_problem_details["slug"],
                    "question_type": first_problem_details["problem_type"],
                    "source": "IMPORTED",
                    "tab_index": 2,
                }
            )
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_QUESTIONS), "POST",
            path_params={"interviewSlug": interview_slug}, query_params=params, body=payload,
            expected_status_code=201,
        )

    def patch_final_status(self, interview_slug: str, status: str = "ON_HOLD") -> requests.Response:
        """Mirrors patch_final_status.py::patch_final_status(shared_data, status)."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_FINAL_STATUS), "PATCH",
            path_params={"interviewSlug": interview_slug}, body=final_status_payload(status),
        )
        assert response.status_code in (200, 202), f"Expected status code 200 or 202, got {response.status_code}"
        return response

    def post_final_status(self, interview_slug: str, status: str = "ON_HOLD") -> requests.Response:
        """
        Mirrors post_final_status.py::post_update_final_status(shared_data, status) — same
        endpoint/payload as patch_final_status, but sent as POST (a distinct source function).
        """
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_FINAL_STATUS), "POST",
            path_params={"interviewSlug": interview_slug}, body=final_status_payload(status),
        )
        assert response.status_code in (200, 202), f"Expected status code 200 or 202, got {response.status_code}"
        return response

    def get_interviewer_feedback(self, interview_slug: str) -> requests.Response:
        """Mirrors get_interviewer_feedback.py::get_interviewer_feedback(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_INTERVIEWER_FEEDBACK), "GET",
            path_params={"interviewSlug": interview_slug}, expected_status_code=200,
        )

    def _resolve_feedback_rating_field(self, interview_slug: str) -> dict:
        """
        `interviewer_feedback_payload`'s default rating_id ("rating57ae2") is a fixed placeholder,
        but the server generates a random-suffixed rating id per job role (e.g. "rating6bc67") when
        the role's scorecard is created — sending an id the role doesn't recognize is what the live
        API rejects with a generic 422 "IF422". `GET .../interviewer_feedback/` returns the actual
        template for this interview's job role, so pull the real id/name/order for "Communication
        Skills" from there (falling back to any other `type: "rating"` entry if that name is ever
        missing), instead of guessing a fixed key.
        """
        template = self.get_interviewer_feedback(interview_slug).json().get("evaluation_ratings", {})
        rating_entries = {key: meta for key, meta in template.items() if meta.get("type") == "rating"}
        rating_id, meta = next(
            ((key, meta) for key, meta in rating_entries.items() if meta.get("name") == "Communication Skills"),
            next(iter(rating_entries.items())),
        )
        return {
            "rating_id": rating_id,
            "rating_name": meta.get("name", "Communication Skills"),
            "rating_type": meta.get("type", "rating"),
            "category": meta.get("category", "default"),
            "order": meta.get("order", 1),
        }

    def post_interviewer_feedback(self, interview_slug: str) -> str:
        """
        Mirrors post_interview_feedback.py::post_interviewer_feedback(shared_data): returns the
        created feedback's slug. Uses the interview's actual rating field (see
        `_resolve_feedback_rating_field`) rather than the payload helper's placeholder id.
        """
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_INTERVIEWER_FEEDBACK), "POST",
            path_params={"interviewSlug": interview_slug},
            body=interviewer_feedback_payload(**self._resolve_feedback_rating_field(interview_slug)),
            expected_status_code=201,
        )
        return response.json().get("slug")

    def patch_interviewer_feedback(
        self, interview_slug: str, interview_feedback_slug: str, rating: int = 5
    ) -> requests.Response:
        """Mirrors patch_interviewer_feedback.py::patch_interviewer_feedback(shared_data, feedback_id, rating)."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_INTERVIEWER_FEEDBACK_DETAIL), "PATCH",
            path_params={"interviewSlug": interview_slug, "feedbackSlug": interview_feedback_slug},
            body=interviewer_feedback_payload(rating=rating, **self._resolve_feedback_rating_field(interview_slug)),
        )
        assert response.status_code in (200, 202), f"Expected status code 200 or 202, got {response.status_code}"
        return response

    def post_ask_feedback(self, interview_slug: str) -> requests.Response:
        """Mirrors post_ask_feedback.py::post_ask_feedback(shared_data) (interviewer_email is always RECRUITER_EMAIL)."""
        payload = ask_feedback_payload("This is a test feedback message", RECRUITER_EMAIL)
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_ASK_FEEDBACK), "POST",
            path_params={"interviewSlug": interview_slug}, body=payload,
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_leave_all(self, interview_slug: str) -> requests.Response:
        """Mirrors post_leave_all.py::post_leave_all(shared_data)."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_LEAVE_ALL), "POST",
            path_params={"interviewSlug": interview_slug},
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_start_interview_as_interviewer(self, interview_slug: str) -> requests.Response:
        """Mirrors post_start_interview_as_interviewer.py::post_start_interview_as_interviewer(shared_data)."""
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_START), "POST",
            path_params={"interviewSlug": interview_slug}, expected_status_code=201,
        )

    def post_instant_interview_login_as_interviewer(self, session_interview_token: str) -> Optional[str]:
        """
        Mirrors post_instant_interview_login_as_interviewer.py: same URL as get_interview_meta,
        but with the source's own (wider) slug-field fallback, kept separate for fidelity.
        """
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_META), "GET",
            path_params={"interviewToken": session_interview_token}, expected_status_code=200,
        )
        data = response.json()
        return data.get("slug") or data.get("interview_slug") or data.get("id")

    # ------------------------------------------------------------------ joining / OTP

    def post_join_interview(
        self,
        interview_slug: str,
        participant_type: str,
        otp: Optional[str] = None,
        participant_name: str = "MyNewCandidate",
        participant_email: Optional[str] = None,
    ) -> requests.Response:
        """
        Mirrors post_join_interview.py::post_join_interview(interview_slug, participant_type,
        shared_data, otp). For CANDIDATE, the source's `generate_params(..., "join_as_candidate_
        in_interview_params", ...)` identifier doesn't match any case in the dispatcher (only
        "join_as_participant_in_interview" does), so it always falls through to `{}` there —
        preserved here as a plain empty base before the explicit `.update()` fields.
        """
        participant_type = participant_type.upper()
        if participant_type == "CANDIDATE":
            payload: dict[str, Any] = {}
            payload.update(
                {
                    "participant_type": "CANDIDATE",
                    "participant_name": participant_name,
                    "participant_email": participant_email or CANDIDATE_EMAIL_INTERVIEW,
                }
            )
            if otp:
                payload["otp"] = otp
        elif participant_type == "INTERVIEWER":
            payload = {"participant_type": "INTERVIEWER"}
        else:
            raise ValueError(f"Invalid participant_type: {participant_type}. Use 'CANDIDATE' or 'INTERVIEWER'.")

        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_JOIN), "POST",
            path_params={"interviewSlug": interview_slug}, body=payload,
        )
        assert response.status_code in (200, 201), (
            f"Join interview failed - Expected status code 200 or 201, got {response.status_code}. "
            f"Response: {response.text}"
        )
        return response

    def post_join_interview_as_interviewer(self, interview_slug: str) -> requests.Response:
        """Mirrors post_join_interview_as_interviewer.py::post_join_interview_as_interviewer(shared_data)."""
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.INTERVIEW_JOIN), "POST",
            path_params={"interviewSlug": interview_slug}, body=create_join_interview_payload(),
        )
        assert response.status_code in (200, 201), (
            f"Join interview failed - Expected status code 200 or 201, got {response.status_code}. "
            f"Response: {response.text}"
        )
        return response

    def post_send_otp(self, full_name: str, email: str, interview_slug: str, interview_token: str) -> requests.Response:
        """
        Mirrors post_send_otp.py::post_send_otp(shared_data, full_name, email, interview_slug,
        interview_token) — `interview_token` is accepted (kept for call-site parity) but, exactly
        as in the source, never actually placed in the payload.
        """
        payload = {
            "full_name": full_name,
            "email": email,
            "interview_slug": interview_slug,
            "participant_type": "CANDIDATE",
        }
        return execute_request(
            self._spec_builder.send_otp_spec(), "POST", body=payload, expected_status_code=200,
        )

    def join_interview_as_candidate_using_otp(
        self, participant_email: str, session_interview_token: str, max_otp_retries: int = 2,
    ) -> dict:
        """
        Mirrors post_join_interview_as_candidate_using_otp.py::join_interview_as_candidate_using_otp.
        `max_otp_retries` is accepted for call-site parity (the source also never actually forwards
        it to get_otp_from_email_helper's own `max_retries`, always using 5 there — preserved).
        """
        participant_name = generate_fake_name()
        interview_slug = self.get_interview_meta(session_interview_token)

        otp_send_response = self.post_send_otp(
            full_name=participant_name, email=participant_email, interview_slug=interview_slug,
            interview_token=session_interview_token,
        )
        if otp_send_response.status_code not in (200, 201):
            return {"status_code": otp_send_response.status_code, "success": False}

        time.sleep(15)

        otp_result = get_otp_from_email_helper(
            subject_to_search="DoSelect Email Verification", max_retries=5, delay_seconds=15,
        )
        if otp_result["status_code"] != 200:
            return {"status_code": otp_result["status_code"], "success": False}

        response = self.post_join_interview(
            interview_slug, "CANDIDATE", otp=otp_result["otp"], participant_name=participant_name,
            participant_email=participant_email,
        )
        return {"status_code": response.status_code, "success": True}

    # ------------------------------------------------------------------ scheduling / cancelling

    def post_schedule_interview(self) -> requests.Response:
        """Mirrors post_schedule_interview.py::post_schedule_interview(shared_data)."""
        job_role_slug = self.get_latest_job_role_slug()
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_SCHEDULE_INTERVIEW), "POST",
            path_params={"jobRoleSlug": job_role_slug}, body=create_schedule_interview_payload(),
        )
        assert response.status_code in (200, 201), f"Expected status code 200 or 201, got {response.status_code}"
        return response

    def post_cancel_interview(self) -> requests.Response:
        """
        Mirrors post_cancel_interview.py::post_cancel_interview(shared_data), except actually
        threading the UPCOMING search's result into the cancel payload. Source calls
        `search_interviews_based_on_status(shared_data, status="UPCOMING")` but never threads its
        result anywhere — `shared_data["interview_slug_upcoming"]` is never set, so the source's
        literal `payload = {"slug": [shared_data.get("interview_slug_upcoming")]}` always ends up
        `{"slug": [None]}`, which the server 400s on ("This field may not be null.", verified live
        against PLT). Fixed here by taking the first UPCOMING result's own `slug`.
        """
        job_role_slug = self.get_latest_job_role_slug()
        search_response = self.search_interviews_based_on_status(status="UPCOMING")
        results = search_response.json().get("results", [])
        if not results:
            raise AssertionError("No UPCOMING interviews found to cancel")
        payload = upcoming_interview_slug_payload(results[0]["slug"])
        return execute_request(
            self._spec_builder.default_spec(interview_api_path.ROLE_CANCEL_INTERVIEW), "POST",
            path_params={"jobRoleSlug": job_role_slug}, body=payload, expected_status_code=200,
        )

    # ------------------------------------------------------------------ interviewer invites

    def post_invite_interviewer(self) -> tuple:
        """
        Mirrors post_invite_interviewer.py::post_invite_interviewer(shared_data): returns
        (email, full_name) directly (source stashed both in shared_data).
        """
        full_name = generate_fake_name()
        email = generate_random_email()
        payload = add_interviewer_payload(full_name, email)
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.RPC_INTERVIEWER_INVITE), "POST", body=payload,
        )
        assert response.status_code in (200, 201), f"Expected status code 200/201, got {response.status_code}"
        return email, full_name

    def delete_invite_interviewer(self, email: Optional[str] = None) -> requests.Response:
        """
        Mirrors delete_invite_interviewer.py::delete_invite_interviewer(shared_data). Source only
        ever builds `payload` inside `if shared_data.get("random_interviewer_email") is not None`
        and otherwise references the undefined local in the `requests.delete(..., json=payload)`
        call right after — a NameError bug when invoked standalone (as
        test_delete_invite_interviewer.py does, with no prior post_invite_interviewer call). Fixed
        here by sending no body when `email` is omitted instead of crashing.
        """
        payload = delete_interviewer_payload(email) if email else None
        response = execute_request(
            self._spec_builder.default_spec(interview_api_path.RPC_INTERVIEWER_INVITE), "DELETE", body=payload,
        )
        assert response.status_code in (200, 204), f"Expected status code 200/204, got {response.status_code}"
        return response
