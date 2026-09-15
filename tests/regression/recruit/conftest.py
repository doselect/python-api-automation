"""
recruit-domain fixtures. Reuses `recruiter_auth_manager` from tests/regression/conftest.py (same
pattern as tests/regression/contest/conftest.py and tests/regression/doiq/conftest.py).

Also provides `hacker_spec_builder`/`hacker_response_handler`/`candidate_session` — duplicated
from tests/regression/hacker/conftest.py rather than imported from it, since pytest conftest
fixtures aren't visible across sibling directories (only down the directory tree) and
tests/regression/hacker/*.py is an already-completed domain not to be modified. Several `recruit`
source tests (test_candidate_report_flow.py, test_extend_test_time.py, test_retakes_flow.py,
test_solutionset_reset_flow.py) call the hacker domain's `test_attempt_mcq` as a setup step and
then read state it populated into `shared_data` (test_slug, candidate_username, solutionset_id,
...); since this port threads data via explicit returns instead of `shared_data`,
`tests/regression/recruit/_mcq_attempt_flow.py` re-implements that same call sequence (using these
fixtures) and returns the state explicitly, rather than depending on
`tests/regression/hacker/test_attempt_mcq.py`'s return value (it has none — see that file).
"""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from src.specs.hacker_spec_builder import CandidateSession, HackerSpecBuilder
from src.specs.recruit_spec_builder import RecruitSpecBuilder


@pytest.fixture
def recruit_spec_builder(recruiter_auth_manager: AuthManager) -> RecruitSpecBuilder:
    return RecruitSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def recruit_response_handler(recruit_spec_builder: RecruitSpecBuilder) -> RecruitResponseHandler:
    return RecruitResponseHandler(recruit_spec_builder)


@pytest.fixture
def candidate_session() -> CandidateSession:
    return CandidateSession()


@pytest.fixture
def hacker_spec_builder(candidate_session: CandidateSession) -> HackerSpecBuilder:
    return HackerSpecBuilder(candidate_session)


@pytest.fixture
def hacker_response_handler(
    hacker_spec_builder: HackerSpecBuilder, candidate_session: CandidateSession
) -> HackerResponseHandler:
    return HackerResponseHandler(hacker_spec_builder, candidate_session)
