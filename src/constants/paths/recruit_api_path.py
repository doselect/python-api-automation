"""
Ports tests/regression_api_methods/recruit/*.py + tests/regression_api_methods/common/
get_test_details.py's "recruiter" branch (https://github.com/doselect/do-api-automation.git).

Started as a minimal 5-endpoint slice added by the `hacker`-porting agent (see the first block of
constants below) so the hacker attempt-flow tests could create/populate a test before switching to
the candidate/test-gateway flow; extended here to cover the remainder of the `recruit` domain.

One path template preserves a literal source quirk rather than "fixing" it:
- `LOCK_ACTION` ends in a literal trailing slash before the query string
  (`/rpc/lock/{lockAction}/`) — copied verbatim from post_create_lock.py's f-string, matching how
  `contest_api_path.py::PROBLEMS_MODIFY`/`ADD_MAX_RETAKES` etc. preserve the same kind of quirk.

`get_test_candidates.py` is the one endpoint in this domain that hits a different host
(`DOLORES_BASE_URL`, not `DOSELECT_PRIMARY_DOMAIN`) — `set_dolores_base_url()` exposes that
separately so `RecruitSpecBuilder.test_candidates_spec()` can use it instead of `set_base_url()`.
"""
from __future__ import annotations

from src.core.do_api_config import DOLORES_BASE_URL, DOSELECT_PRIMARY_DOMAIN

# -- minimal slice (hacker attempt-flow prerequisite; see module docstring) --------------------
TEST_LIST = "/api/v1/test"
TEST_DETAIL = "/api/v1/test/{testSlug}"
PROBLEM_SEARCH = "/search/psearch"
PROBLEMS_MODIFY = "/rpc/problems.modify"
PROBLEM_DETAIL = "/api/v1/problem/{problemSlug}"

# -- rest of the domain --------------------------------------------------------------------------
COMPANY_DETAIL = "/api/v1/company/{companySlug}"
COMPANY_FEEDS = "/stylus/companyfeeds"
COMPANY_INTERACTIONS = "/api/v1/company/{companySlug}/interactions/{email}"
COMPANY_RECRUITERS = "/api/v1/company/{companySlug}/recruiters"
COMPANY_TEAM_INVITES = "/api/v1/company/{companySlug}/teaminvites"
CRUNCH_HACKER_DATA = "/rpc/crunch.hacker_data"
DIRECT_PDF = "/rpc/direct_pdf"
DIRECT_PDF_STATUS = "/rpc/direct_pdf/status/{testSlug}"
GENERIC_LIBRARY = "/generic/api/library"
HACKATHON_COMPANY = "/hackathon-service/api/v1/company/{companySlug}/"
HACKATHON_CONTEST_DETAILS = "/hackathon-service/api/v1/contest/{contestId}/"
HACKATHON_CONTESTS = "/hackathon-service/api/v1/recruit/contest/"
HACKATHON_PARTICIPANT_COUNT_USER_STATE = "/hackathon-service/api/v1/participant/countuserstate"
HACKATHON_PARTICIPANT_VIEW = "/hackathon-service/api/v1/participant/participantview"
HACKATHON_QUOTAS = "/customapi/hackathon/v1/quotas"
INVITE_CREATE = "/rpc/invite.create"
INVITE_DETAIL = "/api/v1/invite/{inviteId}"
LOCK_ACTION = "/rpc/lock/{lockAction}/"
PROCTOR_VERDICT = "/rpc/proctorv2/verdict/fetch/test/{solutionsetId}"
RECRUITER_DETAIL = "/api/v1/recruiter/{recruiterId}"
RETAKES_ADD_MAX = "/rpc/invite.add_max_retakes/"
RETAKES_REMOVE = "/rpc/invite.remove_retakes/"
BULK_REMINDER_CLEAR = "/rpc/bulk_reminder/clear/{reminderId}"
BULK_REMINDER_STATUS = "/rpc/bulk_reminder/status/{reminderId}"
SEND_REMINDER = "/rpc/send_reminder/{testSlug}"
SOLUTION_DETAIL = "/api/v1/solution/{solutionSlug}"
SOLUTION_REVIEW = "/api/v1/solution/{solutionSlug}/review"
SOLUTION_REVISIONS = "/api/v1/solution/{solutionSlug}/revisions"
SOLUTIONSET = "/api/v1/test/{testSlug}/solutionset"
TEAM_MEMBER_STATS = "/rpc/team.get_member_stats"
TEAM_MONTHLY_STATS = "/rpc/team.get_monthly_stats"
TEAM_QUOTAS = "/rpc/billing.get_team_quotas"
TEST_CANDIDATES = "/search/test/{testSlug}/candidates"
TEST_CLONE = "/rpc/test.clone"
TEST_INCREASE_DURATION = "/rpc/test.increase_duration"
TEST_RESET_SOLUTIONSET = "/rpc/test.reset_solutionset/{inviteId}"
TEST_SECTION = "/rpc/test.section"
TEST_TRY_AS_RECRUITER = "/rpc/test.try_as_recruiter"
TEST_REPORT_COMMENT = "/api/v1/testreportcomment"
USER_DETAIL = "/api/v1/user/{username}"
USER_PERMISSIONS = "/rpc/user.get_permissions"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN


def set_dolores_base_url() -> str:
    """Mirrors utils.config.DOLORES_BASE_URL (env var `DOLORES_BASE_URL`) — get_test_candidates.py's host."""
    return DOLORES_BASE_URL
