"""
hacker-domain fixtures. Reuses `recruiter_auth_manager` from tests/regression/conftest.py for the
recruiter-side test setup (post_create_test/get_list_of_problems/post_add_problem/
get_problem_details — see src/responses/recruit_response_handler.py's docstring for scope).

The candidate/hacker side is *not* a login-based AuthManager (see src/specs/hacker_spec_builder.py's
docstring — the source never authenticates the candidate via `/login`; the session is seeded mid-
test from `/gateways/test` cookies once a recruiter-issued access code exists). That means there is
no equivalent of `recruiter_auth_manager` to build up front: `candidate_session` below just hands
each test a fresh, empty `CandidateSession` that `hacker_response_handler.get_test_gateway(...)`/
`post_test_gateway_submit(...)` populate once the flow reaches that point. Kept local to this
conftest (not tests/regression/conftest.py) since it doesn't fit that shared file's "fixture that
authenticates immediately" pattern the way `recruiter_auth_manager` does, and to avoid conflicting
with the parallel `contest`-domain agent's edits to that shared file.
"""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.responses.hacker_response_handler import HackerResponseHandler
from src.responses.recruit_response_handler import RecruitResponseHandler
from src.specs.hacker_spec_builder import CandidateSession, HackerSpecBuilder
from src.specs.recruit_spec_builder import RecruitSpecBuilder


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


@pytest.fixture
def recruit_spec_builder(recruiter_auth_manager: AuthManager) -> RecruitSpecBuilder:
    return RecruitSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def recruit_response_handler(recruit_spec_builder: RecruitSpecBuilder) -> RecruitResponseHandler:
    return RecruitResponseHandler(recruit_spec_builder)
