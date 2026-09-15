"""
Ports the `/hackathon-service/api/v1/contest/*` (+ two `/rpc/*`) endpoints exercised under
tests/regression_api_methods/contest/ + tests/test_regression/test_contest/ in
https://github.com/doselect/do-api-automation.git. Like doiq/ai_interview, these session-auth
endpoints hit `DOSELECT_PRIMARY_DOMAIN` — the same host AuthManager logs into — not `BASE_URL`.

Two path templates preserve literal quirks present in the source rather than "fixing" them:
- `ALL_CONTESTS` ends in a literal `?uuId=` (get_all_contest.py builds the URL with an empty
  trailing `uuId=` *and* passes an actual `uuId` via query params — `requests` merges both onto
  the wire, producing a duplicated `uuId` param, same as the source).
- `LATEST_CONTEST` contains a literal double slash (`api/v1//recruit/contest/`) — copied verbatim
  from get_latest_contest.py's f-string.
- `PROBLEMS_MODIFY` contains a literal `?/` before the contest id (`/rpc/problems.modify?/{id}/`)
  — copied verbatim from post_add_problem.py's f-string.
"""
from __future__ import annotations

from src.core.do_api_config import DOSELECT_PRIMARY_DOMAIN

CONTEST_LIST = "/hackathon-service/api/v1/contest/"
CONTEST_DETAIL = "/hackathon-service/api/v1/contest/{contestId}/"
CONTEST_PHASE_LIST = "/hackathon-service/api/v1/contest/{contestId}/phase/"
CONTEST_PHASE_DETAIL = "/hackathon-service/api/v1/contest/{contestId}/phase/{phaseId}/"
CONTEST_CLONE = "/hackathon-service/api/v1/contest/clone/"
ALL_CONTESTS = "/hackathon-service/api/v1/contest/?uuId="
LATEST_CONTEST = "/hackathon-service/api/v1//recruit/contest/"
PROBLEMS_MODIFY = "/rpc/problems.modify?/{contestId}/"
TEST_SECTION = "/rpc/test.section?contest_id={contestId}"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN
