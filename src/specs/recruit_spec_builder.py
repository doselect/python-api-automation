"""
Ports the header-building side of tests/regression_api_methods/recruit/*.py (do-api-automation).

Started as a minimal 5-endpoint slice (create_test_spec/test_details_spec/search_problems_spec/
add_problem_spec/problem_details_spec) added by the `hacker`-porting agent; extended here to cover
the rest of the domain. Every `get_*_headers`/`get_*_params` function in utils/header_generator.py
that a `recruit` source file references was read directly (not assumed from a pattern) — most
follow one of a few repeated shapes:

- Many GET endpoints reuse the exact `CHROME_WINDOWS_FINGERPRINT_HEADERS` block (sec-ch-ua*/
  sec-fetch-*/user-agent) plus an auth pair + `accept`/`accept-language`/`priority`/`referer` —
  factored into `_fingerprint_headers()` below rather than re-pasted per endpoint.
- Several endpoints (get_recruiter_details.py, get_team_monthly_stats.py, get_team_quotas.py,
  get_search_results.py, and header_generator.py's `get_company_details_headers`) share one more
  literal dict (no sec-ch-ua/priority, just `sec-fetch-*`) with `referer=f"{DOMAIN}/recruit"` —
  factored into `_plain_recruit_headers()`.
- A third shape (`x-csrftoken`/`Cookie`/`accept`/`content-type`/`origin`/`referer`[/`priority`])
  covers the test-edit-problems-referer endpoints (post_create_test.py's `create_test_spec` was
  already ported this way by the hacker-porting agent; post_create_lock.py/
  post_try_test_as_recruiter.py/post_add_section.py/post_create_invite.py reuse the same shape
  with small per-endpoint deltas, built inline per-method to preserve each source file's exact
  deltas rather than force a shared helper that would blur them).

A handful of endpoints build genuinely unique/minimal header dicts in the source (get_proctor_verdict.py:
just the auth pair; get_solutionset.py: auth pair + one `referer`; patch_test_details.py: its own
`if-match` header) — ported as literal one-off dicts, not squeezed into a shared helper.
"""
from __future__ import annotations

from typing import Optional

from src.constants.headers.browser_fingerprint_headers import CHROME_WINDOWS_FINGERPRINT_HEADERS
from src.constants.paths import recruit_api_path
from src.core.auth_manager import AuthManager
from src.core.base_spec_builder import RequestSpec, build_request_spec
from src.core.do_api_config import (
    CANDIDATE_USERNAME_FOR_SOLUTIONSET,
    CONTEST_ID,
    PROCTORING_TEST_SLUG,
    TEST_SLUG_RECRUIT,
)
from src.specs.session_auth_headers import default_recruiter_headers


class RecruitSpecBuilder:
    """Builds the reusable request specs for the ported `recruit` regression endpoints."""

    def __init__(self, auth_manager: AuthManager) -> None:
        self._auth_manager = auth_manager

    # -- shared header shapes -----------------------------------------------------------------

    def _auth_pair(self) -> dict[str, str]:
        return {"x-csrftoken": self._auth_manager.csrf_token, "Cookie": self._auth_manager.cookie}

    def _fingerprint_headers(
        self, accept: str, referer: str, extra: Optional[dict[str, str]] = None
    ) -> dict[str, str]:
        """Mirrors the many `get_*_headers` functions built from accept/accept-language/priority/
        referer + the literal Chrome-Windows fingerprint block."""
        headers = {
            **self._auth_pair(),
            "accept": accept,
            "accept-language": "en-US,en;q=0.9",
            "priority": "u=1, i",
            "referer": referer,
        }
        headers.update(CHROME_WINDOWS_FINGERPRINT_HEADERS)
        if extra:
            headers.update(extra)
        return headers

    def _plain_recruit_headers(self) -> dict[str, str]:
        """Mirrors get_company_details_headers/get_recruiter_details.py/get_team_monthly_stats.py/
        get_team_quotas.py/get_search_results.py's identical inline dict."""
        return {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "referer": f"{recruit_api_path.set_base_url()}/recruit",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }

    def _edit_problems_headers(self, test_slug: Optional[str], priority: bool = True) -> dict[str, str]:
        """Mirrors get_create_candidate_invite_headers/post_create_lock.py/
        post_try_test_as_recruiter.py's `.../test/{slug}/edit/problems` referer shape."""
        headers = {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "origin": recruit_api_path.set_base_url(),
            "referer": f"{recruit_api_path.set_base_url()}/test/{test_slug or '89a8n'}/edit/problems",
        }
        if priority:
            headers["priority"] = "u=1, i"
        return headers

    # -- minimal slice (hacker attempt-flow prerequisite) --------------------------------------

    def create_test_spec(self, test_slug: str | None = None) -> RequestSpec:
        """Mirrors post_create_test.py's headers (`get_create_candidate_invite_headers`)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_LIST,
            headers=self._edit_problems_headers(test_slug),
        )

    def test_details_spec(self) -> RequestSpec:
        """Mirrors get_test_details.py's "recruiter" branch (plain default recruiter headers)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_DETAIL,
            headers=default_recruiter_headers(self._auth_manager),
        )

    def search_problems_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors get_list_of_problems.py's headers (default + `edit/problems` referer override)."""
        headers = default_recruiter_headers(self._auth_manager)
        headers.update({"referer": f"{recruit_api_path.set_base_url()}/test/{test_slug}/edit/problems"})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROBLEM_SEARCH, headers=headers
        )

    def add_problem_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors post_add_problem.py's manually-built headers dict (not via header_generator)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROBLEMS_MODIFY,
            headers=self._edit_problems_headers(test_slug, priority=False),
        )

    def problem_details_spec(self) -> RequestSpec:
        """Mirrors get_problem_details.py's headers (plain default recruiter headers, no overrides)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROBLEM_DETAIL,
            headers=default_recruiter_headers(self._auth_manager),
        )

    # -- company / recruiter / team -------------------------------------------------------------

    def company_detail_spec(self) -> RequestSpec:
        """Mirrors get_company_details.py (GET) + patch_company_details.py (PATCH, get_patch_company_headers)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_DETAIL,
            headers=self._plain_recruit_headers(),
        )

    def patch_company_spec(self) -> RequestSpec:
        """Mirrors patch_company_details.py's `get_patch_company_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/settings/team/profile",
            extra={
                "cache-control": "max-age=0",
                "content-type": "application/json;charset=UTF-8",
                "origin": recruit_api_path.set_base_url(),
            },
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_DETAIL, headers=headers
        )

    def company_feeds_spec(self) -> RequestSpec:
        """Mirrors get_company_feeds.py's manually-built headers."""
        headers = {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "if-none-match": '"3824d217d7468607d11ab8707fe5b36a;gzip"',
            "referer": f"{recruit_api_path.set_base_url()}/recruit",
        }
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_FEEDS, headers=headers
        )

    def company_interactions_spec(self, interaction_email: str) -> RequestSpec:
        """Mirrors get_company_interactions.py's `get_company_interactions_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/interactions?q={interaction_email}"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_INTERACTIONS, headers=headers
        )

    def company_recruiters_spec(self) -> RequestSpec:
        """Mirrors get_company_recruiters.py's `get_company_recruiters_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/settings/team/profile"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_RECRUITERS, headers=headers
        )

    def company_team_invites_spec(self) -> RequestSpec:
        """Mirrors get_company_team_invites.py's `get_company_team_invites_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/settings/team/profile"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.COMPANY_TEAM_INVITES, headers=headers
        )

    def team_member_stats_spec(self) -> RequestSpec:
        """Mirrors get_team_member_stats.py's `get_team_member_stats_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/settings/team/profile"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEAM_MEMBER_STATS, headers=headers
        )

    def team_monthly_stats_spec(self) -> RequestSpec:
        """Mirrors get_team_monthly_stats.py's manually-built headers (matches `_plain_recruit_headers`)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEAM_MONTHLY_STATS,
            headers=self._plain_recruit_headers(),
        )

    def team_quotas_spec(self) -> RequestSpec:
        """Mirrors get_team_quotas.py's manually-built headers (matches `_plain_recruit_headers`)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEAM_QUOTAS,
            headers=self._plain_recruit_headers(),
        )

    def recruiter_detail_spec(self) -> RequestSpec:
        """Mirrors get_recruiter_details.py's manually-built headers (matches `_plain_recruit_headers`)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.RECRUITER_DETAIL,
            headers=self._plain_recruit_headers(),
        )

    def create_team_invite_spec(self) -> RequestSpec:
        """Mirrors post_create_invite.py(type="team")'s `get_create_team_invite_headers` (candidate-invite headers, referer overridden)."""
        headers = self._edit_problems_headers(None)
        headers["referer"] = f"{recruit_api_path.set_base_url()}/settings/team/members"
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.INVITE_CREATE, headers=headers
        )

    def create_candidate_invite_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_create_invite.py(type="candidate")'s `get_create_candidate_invite_headers`."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.INVITE_CREATE,
            headers=self._edit_problems_headers(test_slug),
        )

    def delete_invite_spec(self) -> RequestSpec:
        """Mirrors delete_invite.py's `get_delete_invite_headers` (dispatcher: generate_headers("recruit","delete_invite",...))."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/settings/team/members",
            extra={"content-type": "text/plain;charset=UTF-8", "origin": recruit_api_path.set_base_url()},
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.INVITE_DETAIL, headers=headers
        )

    # -- hackathon / generic library --------------------------------------------------------------

    def hackathon_company_spec(self) -> RequestSpec:
        """Mirrors get_hackathon_company.py's `get_hackathon_company_headers`."""
        headers = self._fingerprint_headers("application/json", f"{recruit_api_path.set_base_url()}/recruit/contests")
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.HACKATHON_COMPANY, headers=headers
        )

    def hackathon_contests_spec(self) -> RequestSpec:
        """Mirrors get_hackathon_contests.py's `get_hackathon_contests_headers`."""
        headers = self._fingerprint_headers("application/json", f"{recruit_api_path.set_base_url()}/recruit/contests")
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.HACKATHON_CONTESTS, headers=headers
        )

    def hackathon_contest_details_spec(self, contest_id) -> RequestSpec:
        """Mirrors get_hackathon_contest_details.py's `get_hackathon_contest_details_headers`."""
        headers = self._fingerprint_headers(
            "application/json", f"{recruit_api_path.set_base_url()}/recruit/contests/{contest_id}/edit/landing"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.HACKATHON_CONTEST_DETAILS,
            headers=headers,
        )

    def hackathon_participant_view_spec(self, contest_id) -> RequestSpec:
        """Mirrors get_hackathon_participant_view.py's `get_hackathon_participant_view_headers`."""
        headers = self._fingerprint_headers(
            "application/json", f"{recruit_api_path.set_base_url()}/recruit/contests/{contest_id}/edit/participant"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.HACKATHON_PARTICIPANT_VIEW,
            headers=headers,
        )

    def hackathon_participant_count_user_state_spec(self, contest_id) -> RequestSpec:
        """Mirrors get_hackathon_participant_count_user_state.py's headers."""
        headers = self._fingerprint_headers(
            "application/json", f"{recruit_api_path.set_base_url()}/recruit/contests/{contest_id}/edit/participant"
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(),
            base_path=recruit_api_path.HACKATHON_PARTICIPANT_COUNT_USER_STATE, headers=headers,
        )

    def hackathon_quotas_spec(self) -> RequestSpec:
        """Mirrors get_hackathon_quotas.py's `get_hackathon_quotas_headers`."""
        headers = self._fingerprint_headers("application/json", f"{recruit_api_path.set_base_url()}/recruit/contests")
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.HACKATHON_QUOTAS, headers=headers
        )

    def generic_library_spec(self, contest_id: str = "3007", phase_id: str = "3165",
                              section_id: str = "a72a6d67f4cd466ab99b2725e95b70eb") -> RequestSpec:
        """Mirrors get_generic_library.py's `get_generic_library_headers`."""
        headers = self._fingerprint_headers(
            "application/json",
            f"{recruit_api_path.set_base_url()}/recruit/contests/{contest_id}/phase/{phase_id}/section/{section_id}/addProblems",
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.GENERIC_LIBRARY, headers=headers
        )

    def user_details_spec(self) -> RequestSpec:
        """Mirrors get_user_details.py's `get_user_details_headers`."""
        headers = self._fingerprint_headers("application/json", f"{recruit_api_path.set_base_url()}/recruit/contests")
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.USER_DETAIL, headers=headers
        )

    def user_permissions_spec(self) -> RequestSpec:
        """Mirrors get_user_permissions.py's `get_user_permissions_headers`."""
        headers = self._fingerprint_headers("application/json", f"{recruit_api_path.set_base_url()}/recruit/contests")
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.USER_PERMISSIONS, headers=headers
        )

    # -- candidates / solutions / reports ----------------------------------------------------------

    def crunch_hacker_data_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_crunch_hacker_data.py (dispatcher: generate_headers("recruit","get_crunch_hacker_data",...))."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*",
            f"{recruit_api_path.set_base_url()}/test/{test_slug or 'default_test_slug'}/edit/candidates",
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.CRUNCH_HACKER_DATA, headers=headers
        )

    def test_report_comment_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_test_report_comment.py (dispatcher: generate_headers("recruit","get_test_report_comment",...))."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*",
            f"{recruit_api_path.set_base_url()}/test/{test_slug or 'default_test_slug'}/edit/candidates",
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_REPORT_COMMENT, headers=headers
        )

    def _candidate_report_referer(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> str:
        return (
            f"{recruit_api_path.set_base_url()}/test/{test_slug or TEST_SLUG_RECRUIT}/candidates/"
            f"{candidate_username or CANDIDATE_USERNAME_FOR_SOLUTIONSET}?problem={problem_slug or '3b80l9'}"
        )

    def solution_spec(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_solution.py (dispatcher: generate_headers("recruit","get_solution",...))."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", self._candidate_report_referer(test_slug, candidate_username, problem_slug)
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.SOLUTION_DETAIL, headers=headers
        )

    def solution_revisions_spec(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_solution_revisions.py's `get_solution_revisions_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", self._candidate_report_referer(test_slug, candidate_username, problem_slug)
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.SOLUTION_REVISIONS, headers=headers
        )

    def solution_review_spec(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> RequestSpec:
        """Mirrors patch_solution_review.py's `get_solution_review_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", self._candidate_report_referer(test_slug, candidate_username, problem_slug),
            extra={"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()},
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.SOLUTION_REVIEW, headers=headers
        )

    def direct_pdf_spec(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_direct_pdf.py's `get_direct_pdf_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", self._candidate_report_referer(test_slug, candidate_username, problem_slug),
            extra={"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()},
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.DIRECT_PDF, headers=headers
        )

    def direct_pdf_status_spec(self, test_slug: Optional[str], candidate_username: Optional[str], problem_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_direct_pdf_status.py's `get_direct_pdf_status_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", self._candidate_report_referer(test_slug, candidate_username, problem_slug)
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.DIRECT_PDF_STATUS, headers=headers
        )

    def solutionset_spec(self) -> RequestSpec:
        """
        Mirrors get_solutionset.py's manually-built headers. The source hardcodes
        `PROCTORING_TEST_SLUG`/`CANDIDATE_USERNAME_FOR_SOLUTIONSET` for the referer (ignoring
        `shared_data`), preserved as-is (see RecruitResponseHandler.get_solutionset's docstring).
        """
        headers = {
            **self._auth_pair(),
            "referer": (
                f"{recruit_api_path.set_base_url()}/test/{PROCTORING_TEST_SLUG}/candidates/"
                f"{CANDIDATE_USERNAME_FOR_SOLUTIONSET}"
            ),
        }
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.SOLUTIONSET, headers=headers
        )

    def proctor_verdict_spec(self) -> RequestSpec:
        """Mirrors get_proctor_verdict.py's minimal headers (auth pair only)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROCTOR_VERDICT,
            headers=self._auth_pair(),
        )

    def test_candidates_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors get_test_candidates.py's manually-built headers (DOLORES_BASE_URL host, not DOSELECT_PRIMARY_DOMAIN)."""
        headers = {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "referer": f"{recruit_api_path.set_base_url()}/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
        }
        return build_request_spec(
            base_url=recruit_api_path.set_dolores_base_url(), base_path=recruit_api_path.TEST_CANDIDATES,
            headers=headers,
        )

    # -- problem search / results -------------------------------------------------------------

    def problem_search_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_problem_search.py's manually-built headers (distinct from `search_problems_spec`)."""
        headers = {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "if-none-match": '"b78d79c80bd3ca122c3a1cd63da85603;gzip"',
            "referer": f"{recruit_api_path.set_base_url()}/test/{test_slug or '89a8n'}/edit/problems",
        }
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROBLEM_SEARCH, headers=headers
        )

    def search_results_spec(self) -> RequestSpec:
        """Mirrors get_search_results.py's manually-built headers (matches `_plain_recruit_headers`)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.PROBLEM_SEARCH,
            headers=self._plain_recruit_headers(),
        )

    # -- test lifecycle: lock / try-as-recruiter / clone / sections / patch --------------------

    def create_lock_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors post_create_lock.py's manually-built headers."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.LOCK_ACTION,
            headers=self._edit_problems_headers(test_slug),
        )

    def try_test_as_recruiter_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors post_try_test_as_recruiter.py's manually-built headers."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_TRY_AS_RECRUITER,
            headers=self._edit_problems_headers(test_slug),
        )

    def post_add_section_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_add_section.py's manually-built headers (no `priority` field)."""
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_SECTION,
            headers=self._edit_problems_headers(test_slug, priority=False),
        )

    def clone_test_spec(self) -> RequestSpec:
        """Mirrors post_clone_test.py's `get_clone_test_headers`."""
        headers = self._fingerprint_headers(
            "application/json, text/plain, */*", f"{recruit_api_path.set_base_url()}/recruit/tests",
            extra={"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()},
        )
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_CLONE, headers=headers
        )

    def patch_test_details_spec(self, test_slug: str) -> RequestSpec:
        """Mirrors patch_test_details.py's manually-built headers."""
        headers = {
            **self._auth_pair(),
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json;charset=UTF-8",
            "origin": recruit_api_path.set_base_url(),
            "referer": f"{recruit_api_path.set_base_url()}/test/{test_slug}/edit/general",
            "if-match": '"92fb7821952389db4422d305d38d07ae;gzip"',
        }
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_DETAIL, headers=headers
        )

    # -- retakes / duration / solutionset reset / reminders -------------------------------------

    def _candidates_editor_headers(self, test_slug: Optional[str], referer_override: Optional[str] = None) -> dict[str, str]:
        """Mirrors the common `.../test/{slug}/edit/candidates` POST-header shape shared by
        post_increase_test_duration.py/post_reset_test_solutionset.py/post_remove_retakes.py/
        post_clear_bulk_reminder.py/post_send_reminder.py/get_bulk_reminder_status.py (GET variant
        adds no content-type/origin, added by the caller when needed)."""
        referer = referer_override or f"{recruit_api_path.set_base_url()}/test/{test_slug or TEST_SLUG_RECRUIT}/edit/candidates"
        return self._fingerprint_headers("application/json, text/plain, */*", referer)

    def add_max_retakes_spec(self) -> RequestSpec:
        """Mirrors post_add_max_retakes.py's `get_add_max_retakes_headers` — referer is a literal
        `/test/4wa3a/edit/candidates`, not derived from `test_slug`, preserved as-is."""
        headers = self._candidates_editor_headers(
            None, referer_override=f"{recruit_api_path.set_base_url()}/test/4wa3a/edit/candidates"
        )
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.RETAKES_ADD_MAX, headers=headers
        )

    def remove_retakes_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_remove_retakes.py's `get_remove_retakes_headers`."""
        headers = self._candidates_editor_headers(test_slug)
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.RETAKES_REMOVE, headers=headers
        )

    def increase_test_duration_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_increase_test_duration.py's `get_increase_test_duration_headers`."""
        headers = self._candidates_editor_headers(test_slug)
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_INCREASE_DURATION,
            headers=headers,
        )

    def reset_test_solutionset_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_reset_test_solutionset.py's `get_reset_test_solutionset_headers`."""
        headers = self._candidates_editor_headers(test_slug)
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.TEST_RESET_SOLUTIONSET,
            headers=headers,
        )

    def bulk_reminder_status_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors get_bulk_reminder_status.py's `get_bulk_reminder_status_headers` (GET, no content-type/origin)."""
        headers = self._candidates_editor_headers(test_slug)
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.BULK_REMINDER_STATUS,
            headers=headers,
        )

    def clear_bulk_reminder_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_clear_bulk_reminder.py's `get_clear_bulk_reminder_headers`."""
        headers = self._candidates_editor_headers(test_slug)
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.BULK_REMINDER_CLEAR,
            headers=headers,
        )

    def send_reminder_spec(self, test_slug: Optional[str]) -> RequestSpec:
        """Mirrors post_send_reminder.py's `get_send_reminder_headers`."""
        headers = self._candidates_editor_headers(test_slug)
        headers.update({"content-type": "application/json;charset=UTF-8", "origin": recruit_api_path.set_base_url()})
        return build_request_spec(
            base_url=recruit_api_path.set_base_url(), base_path=recruit_api_path.SEND_REMINDER, headers=headers
        )
