"""
Ports tests/regression_api_methods/contest/*.py (do-api-automation): one method per source
function, executed through src.core.rest_client.execute_request instead of raw `requests` calls +
manual try/except/finally logging (see doiq_response_handler.py's docstring — same rationale).
Every real `assert` the source makes is preserved, including the multi-condition
`get_all_contest.py` assert and the retry-then-assert idiom used by nearly every `patch_*`
function (PATCH once unasserted; on non-200, create a fresh contest and PATCH again; assert 200
only after that).

`shared_data` threading is replaced with explicit return values/parameters throughout, matching
the ai_interview precedent:
- `get_phase_details` returns `phase_id`/`context_slug`/`section_slug` directly (source mutated
  `shared_data` with these as a side effect; callers here receive them in the returned dict).
- `post_create_contest`/`post_create_team_contest`/`post_create_2phase_normal_contest`/
  `post_create_2phase_team_contest` return the created `contestId` directly (source stashed it in
  `shared_data["contest_id"]`).
- `post_add_remove_problem_section` additionally returns the `section_slug` it read off the
  freshly-fetched phase (via its own `get_phase_details` call) so a caller doing an "add" then a
  "delete" of the same section can thread it through explicitly — mirrors
  test_add_nremove_problem_section.py's `section_slug=shared_data["section_slug"]` second call.

Two source quirks are preserved exactly rather than "fixed" (see DO_API_PORT_STATUS.md):
- `get_latest_contest.py::get_latest_contest_id`: when no contests exist, the source creates one
  via `post_create_contest(shared_data)` but then falls through to its trailing
  `return {"status_code": response.status_code}` — the *original* (contest-list) GET's status, a
  dict, not the newly created contest's id. `get_contest_details` calls this and only guards with
  `if not contest_id`, which a non-empty dict still passes (dicts are truthy), so the dict would
  propagate into an f-string URL there too, exactly as it does in the source. Preserved verbatim.
- `convert_2phase_to_1phase_contest.py::convert_2phase_to_1phase`: in the "only one phase, create
  a new 2-phase contest" branch, the final `response` used for the return value is always the
  *GET* of the new contest (`new_response`), never the phase-DELETE response, even when a second
  phase was found and deleted. Preserved verbatim.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pytz
import requests

from src.core.rest_client import execute_request
from src.helpers.contest.payloads import (
    ADD_SECTION_PAYLOAD,
    DELETE_SECTION_PAYLOAD,
    add_criteria_payload,
    add_email_and_phone_number_payload,
    add_only_email_payload,
    add_only_phone_number_payload,
    add_problem_payload,
    add_redirection_url_payload,
    add_theme_section_payload,
    add_three_section_theme_prize_and_eligibility_criteria_section_payload,
    add_two_section_theme_and_prize_section_payload,
    archive_contest_payload,
    clone_contest_payload,
    create_2phase_contest_payload,
    create_2phase_team_contest_payload,
    create_contest_payload,
    create_team_contest_payload,
    delete_custom_form_payload,
    hide_question_name_payload,
    make_section_private_payload,
    mcq_shuffle_payload,
    proctor_settings_payload,
    publish_contest_payload,
    remove_only_prize_section_payload,
    remove_redirection_url_payload,
    remove_three_section_theme_prize_eligibility_section_payload,
    remove_two_section_theme_and_eligibility_section_payload,
    section_name_payload,
    update_access_type_payload,
    update_contest_instruction_payload,
    update_contest_name_payload,
    update_contest_payload,
    update_contest_type_payload,
    update_participant_data_settings_payload,
    update_participation_type_payload,
)
from src.specs.contest_spec_builder import ContestSpecBuilder

_DEFAULT_UUID = "1744108799898"


def _hackathon_contest_details_params() -> dict:
    """Mirrors get_hackathon_contest_details_params(shared_data) — shared_data never overrides
    "contest_details_uuid" at any contest domain call site, so the fallback literal always applies."""
    return {"uuId": _DEFAULT_UUID}


def _patch_hackathon_contest_params() -> dict:
    """Mirrors get_patch_hackathon_contest_params(shared_data) — "patch_hackathon_contest_uuid" is
    never overridden either."""
    return {"uuId": _DEFAULT_UUID}


def _create_hackathon_contest_params() -> dict:
    """Mirrors get_create_hackathon_contest_params(shared_data) — "create_hackathon_contest_uuid"
    is never overridden either."""
    return {"uuId": _DEFAULT_UUID}


class ContestResponseHandler:
    """Wraps a ContestSpecBuilder to centralize the ported `contest` regression API calls."""

    def __init__(self, spec_builder: ContestSpecBuilder) -> None:
        self._spec_builder = spec_builder

    # -------------------------------------------------------------------------------------
    # get_latest_contest.py / get_all_contest.py / get_contest_details.py / get_phase_details.py
    # -------------------------------------------------------------------------------------

    def get_latest_contest_id(self):
        """Mirrors get_latest_contest.py::get_latest_contest_id(shared_data)."""
        response = execute_request(
            self._spec_builder.latest_contest_spec(), "GET", query_params=_hackathon_contest_details_params()
        )
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        try:
            response_data = response.json() if response.text else {}
        except Exception:
            response_data = {"raw_response": response.text}
        contests = response_data.get("data", {}).get("contests", [])
        if contests:
            contest_id = contests[0].get("contestId")
            if contest_id:
                return contest_id
        # No contests found — mirrors the source's own quirk: it creates one but still falls
        # through to returning the *original* GET's status dict rather than the new contest id.
        self.post_create_contest()
        return {"status_code": response.status_code}

    def get_all_contests(self) -> dict:
        """Mirrors get_all_contest.py::get_all_contests(shared_data)."""
        response = execute_request(
            self._spec_builder.all_contests_spec(), "GET", query_params=_hackathon_contest_details_params()
        )
        response_data = response.json()
        total_contest_count = response_data["meta"]["maxDocsInEachPage"]
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        assert total_contest_count == 10, f"Expected total contest count 10, got {total_contest_count}"
        return {"status_code": response.status_code}

    def get_contest_details(self) -> dict:
        """Mirrors get_contest_details.py::get_contest_details(shared_data)."""
        contest_id = self.get_latest_contest_id()
        if not contest_id:
            return {"status_code": 400, "error": "Failed to get contest ID"}
        params = _hackathon_contest_details_params()
        params.update({"contest_id": contest_id})
        response = execute_request(
            self._spec_builder.contest_detail_spec(), "GET",
            path_params={"contestId": contest_id}, query_params=params,
        )
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    def get_phase_details(self) -> dict:
        """
        Mirrors get_phase_details.py::get_phase_details(shared_data). Returns `phase_id`,
        `context_slug`, `section_slug` directly (source stashed these in `shared_data`).
        """
        contest_id = self.get_latest_contest_id()
        response = execute_request(
            self._spec_builder.contest_detail_spec(), "GET",
            path_params={"contestId": contest_id}, query_params=_patch_hackathon_contest_params(),
        )
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        phase_id = context_slug = section_slug = None
        try:
            phases = response.json().get("data", {}).get("phases", [])
            if phases:
                phase_id = phases[0].get("phaseId")
                context_slug = phases[0].get("testSlug")
                section_slug = phases[0].get("sections", [{}])[0].get("slug")
        except Exception:
            pass  # mirrors the source's broad `except Exception` around phase extraction
        return {
            "status_code": response.status_code,
            "phase_id": phase_id,
            "context_slug": context_slug,
            "section_slug": section_slug,
        }

    # -------------------------------------------------------------------------------------
    # convert_1phase_to_2phase_contest.py / convert_2phase_to_1phase_contest.py
    # -------------------------------------------------------------------------------------

    def convert_1phase_to_2phase(self) -> dict:
        """Mirrors convert_1phase_to_2phase_contest.py::convert_1phase_to_2phase(shared_data)."""
        contest_id = self.get_latest_contest_id()
        params = _patch_hackathon_contest_params()
        response = execute_request(
            self._spec_builder.contest_detail_spec(), "GET",
            path_params={"contestId": contest_id}, query_params=params,
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json().get("data", {})
        phases = data.get("phases", [])
        phase_count = data.get("phaseCount", 0)
        timezone = data.get("timezone", "Asia/Kolkata")
        ist = pytz.timezone(timezone)

        if phase_count == 2:
            self.post_create_team_contest()
            contest_id = self.get_latest_contest_id()
            response = execute_request(
                self._spec_builder.contest_detail_spec(), "GET",
                path_params={"contestId": contest_id}, query_params=params,
            )
            assert response.status_code == 200, (
                f"Expected 200 after new contest creation, got {response.status_code}"
            )
            data = response.json().get("data", {})
            phases = data.get("phases", [])
            phase_count = data.get("phaseCount", 0)
            timezone = data.get("timezone", "Asia/Kolkata")
            ist = pytz.timezone(timezone)

        last_phase = phases[-1]
        last_phase_end = datetime.strptime(last_phase["phaseEndTime"], "%Y-%m-%d %H:%M:%S")
        last_phase_end = ist.localize(last_phase_end) if last_phase_end.tzinfo is None else last_phase_end
        new_phase_start = last_phase_end + timedelta(hours=24)
        new_phase_end = new_phase_start + timedelta(hours=24)
        new_phase = {
            "phaseStartTime": new_phase_start.strftime("%Y-%m-%d %H:%M:%S"),
            "phaseEndTime": new_phase_end.strftime("%Y-%m-%d %H:%M:%S"),
            "order": phase_count + 1,
        }
        response = execute_request(
            self._spec_builder.contest_phase_list_spec(), "POST",
            path_params={"contestId": contest_id}, query_params=params, body=new_phase,
            expected_status_code=201,
        )
        return {"status_code": response.status_code}

    def convert_2phase_to_1phase(self) -> dict:
        """Mirrors convert_2phase_to_1phase_contest.py::convert_2phase_to_1phase(shared_data)."""
        contest_id = self.get_latest_contest_id()
        params = _patch_hackathon_contest_params()
        response = execute_request(
            self._spec_builder.contest_detail_spec(), "GET",
            path_params={"contestId": contest_id}, query_params=params,
        )
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        data = response.json().get("data", {})
        phases = data.get("phases", [])
        phase_count = data.get("phaseCount", 0)

        if phase_count > 1 and len(phases) > 1:
            phase_id2 = phases[1].get("phaseId")
            response = execute_request(
                self._spec_builder.contest_phase_detail_spec(), "DELETE",
                path_params={"contestId": contest_id, "phaseId": phase_id2}, query_params=params,
                expected_status_code=204,
            )
        else:
            self.post_create_2phase_normal_contest()
            new_contest_id = self.get_latest_contest_id()
            new_response = execute_request(
                self._spec_builder.contest_detail_spec(), "GET",
                path_params={"contestId": new_contest_id}, query_params=params,
            )
            assert new_response.status_code == 200, f"Expected status code 200, got {new_response.status_code}"
            new_data = new_response.json().get("data", {})
            new_phases = new_data.get("phases", [])
            if len(new_phases) > 1:
                phase_id2 = new_phases[1].get("phaseId")
                execute_request(
                    self._spec_builder.contest_phase_detail_spec(), "DELETE",
                    path_params={"contestId": new_contest_id, "phaseId": phase_id2}, query_params=params,
                    expected_status_code=204,
                )
            response = new_response  # mirrors the source: always the GET response, not the DELETE
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # Shared PATCH-with-retry helper for `.../contest/{contestId}/` PATCH endpoints
    # -------------------------------------------------------------------------------------

    def _patch_contest(self, contest_id, payload: dict) -> requests.Response:
        return execute_request(
            self._spec_builder.contest_detail_spec(), "PATCH",
            path_params={"contestId": contest_id}, query_params=_patch_hackathon_contest_params(), body=payload,
        )

    def _patch_contest_with_retry(self, payload: dict) -> dict:
        """
        Shared retry idiom used by every phase-independent `patch_*` source function: PATCH the
        latest contest; on a non-200, create a fresh contest and PATCH it with the *same* payload
        (source never rebuilds the payload in this branch, only fetches a new contest id); assert
        200 only after that.
        """
        contest_id = self.get_latest_contest_id()
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            response = self._patch_contest(new_contest_id, payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # patch_add_criteria.py (uses the phase-detail endpoint, not contest-detail)
    # -------------------------------------------------------------------------------------

    def patch_add_criteria(self) -> dict:
        """Mirrors patch_add_criteria.py::patch_add_criteria(shared_data)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details()["phase_id"]
        params = _patch_hackathon_contest_params()
        payload = add_criteria_payload()
        response = execute_request(
            self._spec_builder.contest_phase_detail_spec(), "PATCH",
            path_params={"contestId": contest_id, "phaseId": phase_id}, query_params=params, body=payload,
        )
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details()["phase_id"]
            response = execute_request(
                self._spec_builder.contest_phase_detail_spec(), "PATCH",
                path_params={"contestId": new_contest_id, "phaseId": new_phase_id}, query_params=params, body=payload,
            )
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # Phase-independent patch_*.py functions (generic retry, payload reused verbatim)
    # -------------------------------------------------------------------------------------

    def patch_add_participant_data_settings(self) -> dict:
        """Mirrors patch_add_custom_form.py::patch_add_participant_data_settings(shared_data)."""
        return self._patch_contest_with_retry(update_participant_data_settings_payload())

    def patch_add_theme_section(self) -> dict:
        """Mirrors patch_add_only_theme_section.py::patch_add_theme_section(shared_data)."""
        return self._patch_contest_with_retry(add_theme_section_payload())

    def patch_add_three_section_theme_prize_and_eligibility_criteria_section(self) -> dict:
        """Mirrors patch_add_three_section_theme_prize_and_eligibiliy_criteria_section.py's function."""
        return self._patch_contest_with_retry(add_three_section_theme_prize_and_eligibility_criteria_section_payload())

    def patch_add_two_section_theme_and_prize_section(self) -> dict:
        """Mirrors patch_add_two_section_theme_and_prize_section.py's function."""
        return self._patch_contest_with_retry(add_two_section_theme_and_prize_section_payload())

    def patch_archive_contest(self) -> dict:
        """Mirrors patch_archive_contest.py::patch_archive_contest(shared_data)."""
        return self._patch_contest_with_retry(archive_contest_payload())

    def patch_delete_participant_data_settings(self) -> dict:
        """Mirrors patch_delete_custom_form.py::patch_delete_participant_data_settings(shared_data)."""
        return self._patch_contest_with_retry(delete_custom_form_payload())

    def patch_make_section_private(self) -> dict:
        """Mirrors patch_make_prize_and_eligibility_section_private.py::patch_make_section_private(shared_data)."""
        return self._patch_contest_with_retry(make_section_private_payload())

    def patch_remove_only_prize_section(self) -> dict:
        """Mirrors patch_remove_only_prize_section.py::patch_remove_only_prize_section(shared_data)."""
        return self._patch_contest_with_retry(remove_only_prize_section_payload())

    def patch_remove_three_section_theme_prize_eligibility_section(self) -> dict:
        """Mirrors patch_remove_three_section_theme_prize_eligibility_section.py's function."""
        return self._patch_contest_with_retry(remove_three_section_theme_prize_eligibility_section_payload())

    def patch_remove_two_section_theme_and_eligibility_section(self) -> dict:
        """Mirrors patch_remove_two_section_theme_and_eligibility_section.py's function."""
        return self._patch_contest_with_retry(remove_two_section_theme_and_eligibility_section_payload())

    def patch_update_about_us_about_contest(self) -> dict:
        """Mirrors patch_update_about_us_about_contest.py::patch_update_about_us_about_contest(shared_data)."""
        return self._patch_contest_with_retry(update_contest_payload())

    def patch_update_access_type(self, access_type: str) -> dict:
        """Mirrors patch_update_access_type.py::patch_update_access_type(shared_data, access_type)."""
        return self._patch_contest_with_retry(update_access_type_payload(access_type))

    def patch_update_instruction(self) -> dict:
        """Mirrors patch_update_contest_instruction.py::patch_update_instruction(shared_data)."""
        return self._patch_contest_with_retry(update_contest_instruction_payload())

    def patch_update_contest_name(self) -> dict:
        """Mirrors patch_update_contest_name.py::patch_update_contest_name(shared_data)."""
        return self._patch_contest_with_retry(update_contest_name_payload())

    def patch_update_contest_type(self, contest_type: str) -> dict:
        """Mirrors patch_update_contest_type.py::patch_update_contest_type(shared_data, contest_type)."""
        return self._patch_contest_with_retry(update_contest_type_payload(contest_type))

    def patch_update_participation_type(self, participation_type: str, min_team_size, max_team_size) -> dict:
        """Mirrors patch_update_participation_type.py::patch_update_participation_type(...)."""
        return self._patch_contest_with_retry(
            update_participation_type_payload(participation_type, min_team_size, max_team_size)
        )

    # -------------------------------------------------------------------------------------
    # Phase-dependent patch_*.py functions (payload embeds phase_id; retry rebuilds payload
    # with a freshly-fetched phase_id, matching each source function precisely)
    # -------------------------------------------------------------------------------------

    def patch_proctor_settings(
        self,
        proctor_enabled: Optional[bool] = None,
        snapshot_enabled: Optional[bool] = None,
        video_enabled: Optional[bool] = None,
        plagiarism_enabled: Optional[bool] = None,
    ) -> dict:
        """Mirrors patch_add_proctor_settings.py::patch_proctor_settings(shared_data, ...)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details().get("phase_id")
        payload = proctor_settings_payload(phase_id, proctor_enabled, snapshot_enabled, video_enabled, plagiarism_enabled)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details().get("phase_id")
            new_payload = proctor_settings_payload(
                new_phase_id, proctor_enabled, snapshot_enabled, video_enabled, plagiarism_enabled
            )
            response = self._patch_contest(new_contest_id, new_payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    def patch_add_remove_redirection_url(self, action: str = "add") -> dict:
        """Mirrors patch_add_remove_redirection_url.py::patch_add_remove_redirection_url(shared_data, action)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details().get("phase_id")
        payload = add_redirection_url_payload(phase_id) if action == "add" else remove_redirection_url_payload(phase_id)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details().get("phase_id")
            payload = (
                add_redirection_url_payload(new_phase_id)
                if action == "add"
                else remove_redirection_url_payload(new_phase_id)
            )
            response = self._patch_contest(new_contest_id, payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    def patch_mcq_shuffle(self, mcq_option_shuffle) -> dict:
        """Mirrors patch_mcq_shuffle.py::patch_mcq_shuffle(shared_data, MCQ_option_shuffle)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details().get("phase_id")
        payload = mcq_shuffle_payload(phase_id, mcq_option_shuffle)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details().get("phase_id")
            new_payload = mcq_shuffle_payload(new_phase_id, mcq_option_shuffle)
            response = self._patch_contest(new_contest_id, new_payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    def patch_question_name_visibility(self, problem_visibility) -> dict:
        """Mirrors patch_question_name_visibility.py::patch_question_name_visibility(shared_data, problem_visibility)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details().get("phase_id")
        payload = hide_question_name_payload(phase_id, problem_visibility)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details().get("phase_id")
            new_payload = hide_question_name_payload(new_phase_id, problem_visibility)
            response = self._patch_contest(new_contest_id, new_payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    def patch_section_name_visibility(self, section_visibility) -> dict:
        """Mirrors patch_section_name_visibility.py::patch_section_name_visibility(shared_data, section_visibility)."""
        contest_id = self.get_latest_contest_id()
        phase_id = self.get_phase_details().get("phase_id")
        payload = section_name_payload(phase_id, section_visibility)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            new_phase_id = self.get_phase_details().get("phase_id")
            new_payload = section_name_payload(new_phase_id, section_visibility)
            response = self._patch_contest(new_contest_id, new_payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # patch_add_support_details.py (action-branch payload selection, no phase dependency)
    # -------------------------------------------------------------------------------------

    @staticmethod
    def _support_details_payload(show_contact, action: str):
        """
        Mirrors the action-branch payload selection in patch_add_support_details.py. Every call
        site passes action="both"/"email"/"phone"; the source leaves `payload` unassigned (an
        UnboundLocalError waiting to happen) for any other action — never exercised in practice,
        so this returns None for that unreachable branch instead of replicating the crash.
        """
        if action == "both":
            return add_email_and_phone_number_payload(show_contact)
        if action == "email":
            return add_only_email_payload(show_contact)
        if action == "phone":
            return add_only_phone_number_payload(show_contact)
        return None

    def patch_add_support_details(self, show_contact, action: str = "") -> dict:
        """Mirrors patch_add_support_details.py::patch_add_support_details(shared_data, show_contact, action)."""
        contest_id = self.get_latest_contest_id()
        payload = self._support_details_payload(show_contact, action)
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            payload = self._support_details_payload(show_contact, action)
            response = self._patch_contest(new_contest_id, payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # patch_publish_contest.py — retry branch also re-sets-up About-Us + adds a problem
    # -------------------------------------------------------------------------------------

    def patch_publish_contest(self) -> dict:
        """Mirrors patch_publish_contest.py::patch_publish_contest(shared_data)."""
        contest_id = self.get_latest_contest_id()
        payload = publish_contest_payload()
        response = self._patch_contest(contest_id, payload)
        if response.status_code != 200:
            self.post_create_contest()
            self.patch_update_about_us_about_contest()
            self.post_add_problem()
            new_contest_id = self.get_latest_contest_id()
            response = self._patch_contest(new_contest_id, payload)
        assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # post_add_problem.py / post_add_remove_problem_section.py / post_clone_contest.py
    # -------------------------------------------------------------------------------------

    def post_add_problem(self) -> dict:
        """Mirrors post_add_problem.py::post_add_problem(shared_data)."""
        contest_id = self.get_latest_contest_id()
        phase_detail = self.get_phase_details()
        env = ""  # mirrors `shared_data.get("env", "")` — never set at any contest call site
        problem_slug = "godryp" if env == "production" else "leegr"
        payload = add_problem_payload(
            section_slug=phase_detail.get("section_slug"), context_slug=phase_detail.get("context_slug"),
        )
        payload["problem_slug"] = problem_slug
        response = execute_request(
            self._spec_builder.problems_modify_spec(), "POST",
            path_params={"contestId": contest_id}, query_params=_create_hackathon_contest_params(), body=payload,
            expected_status_code=202,
        )
        return {"status_code": response.status_code}

    def _post_test_section(self, contest_id, phase_detail: dict, action: str, section_slug: Optional[str]) -> requests.Response:
        payload = (ADD_SECTION_PAYLOAD if action == "add" else DELETE_SECTION_PAYLOAD).copy()
        if section_slug:
            payload["section_slug"] = section_slug
        payload["test_slug"] = phase_detail["context_slug"]
        return execute_request(
            self._spec_builder.test_section_spec(), "POST",
            path_params={"contestId": contest_id}, query_params=_create_hackathon_contest_params(), body=payload,
        )

    def post_add_remove_problem_section(self, action: str = "add", section_slug: Optional[str] = None) -> dict:
        """
        Mirrors post_add_remove_problem_section.py::post_add_remove_problem_section(shared_data,
        action, section_slug). Also returns the `section_slug` read off the phase fetched during
        this call, so a caller can thread it into a follow-up "delete" call the way the source
        threads `shared_data["section_slug"]`.

        `get_latest_contest_id()` is a company-wide "most recent contest" pointer, not scoped to a
        contest this call created itself — if it resolves to a stale/older contest (e.g. this test
        runs before anything else has created one in this session), the section POST 404s. Retries
        against a freshly-created contest on failure, matching the same idiom every other
        phase-dependent `patch_*` method here already uses (see `patch_proctor_settings` etc.)
        instead of asserting on the first, possibly-stale attempt.
        """
        contest_id = self.get_latest_contest_id()
        phase_detail = self.get_phase_details()
        response = self._post_test_section(contest_id, phase_detail, action, section_slug)
        if response.status_code != 202:
            self.post_create_contest()
            new_contest_id = self.get_latest_contest_id()
            phase_detail = self.get_phase_details()
            response = self._post_test_section(new_contest_id, phase_detail, action, section_slug)
        assert response.status_code == 202, f"Expected status code 202, got {response.status_code}"
        return {"status_code": response.status_code, "section_slug": phase_detail.get("section_slug")}

    def post_clone_contest(self) -> dict:
        """Mirrors post_clone_contest.py::post_clone_contest(shared_data)."""
        contest_id = self.get_latest_contest_id()
        payload = clone_contest_payload(contest_id)
        response = execute_request(
            self._spec_builder.contest_clone_spec(), "POST",
            query_params=_create_hackathon_contest_params(), body=payload, expected_status_code=201,
        )
        return {"status_code": response.status_code}

    # -------------------------------------------------------------------------------------
    # post_create_contest.py / post_create_team_contest.py / post_create_2phase_*.py
    # -------------------------------------------------------------------------------------

    def post_create_contest(self) -> Optional[str]:
        """Mirrors post_create_contest.py::post_create_contest(shared_data) — returns the new contestId."""
        response = execute_request(
            self._spec_builder.contest_list_spec(), "POST",
            query_params=_create_hackathon_contest_params(), body=create_contest_payload(),
            expected_status_code=201,
        )
        return response.json().get("data", {}).get("contestId")

    def post_create_team_contest(self) -> Optional[str]:
        """Mirrors post_create_team_contest.py::post_create_team_contest(shared_data)."""
        response = execute_request(
            self._spec_builder.contest_list_spec(), "POST",
            query_params=_create_hackathon_contest_params(), body=create_team_contest_payload(),
            expected_status_code=201,
        )
        return response.json().get("data", {}).get("contestId")

    def post_create_2phase_normal_contest(self) -> Optional[str]:
        """Mirrors post_create_2phase_normal_contest.py::post_create_2phase_normal_contest(shared_data)."""
        response = execute_request(
            self._spec_builder.contest_list_spec(), "POST",
            query_params=_create_hackathon_contest_params(), body=create_2phase_contest_payload(),
            expected_status_code=201,
        )
        return response.json().get("data", {}).get("contestId")

    def post_create_2phase_team_contest(self) -> Optional[str]:
        """Mirrors post_create_2phase_team_contest.py::post_create_2phase_team_contest(shared_data)."""
        response = execute_request(
            self._spec_builder.contest_list_spec(), "POST",
            query_params=_create_hackathon_contest_params(), body=create_2phase_team_contest_payload(),
            expected_status_code=201,
        )
        return response.json().get("data", {}).get("contestId")
