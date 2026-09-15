"""contest-domain fixtures. Reuses `recruiter_auth_manager` from tests/regression/conftest.py."""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.responses.contest_response_handler import ContestResponseHandler
from src.specs.contest_spec_builder import ContestSpecBuilder


@pytest.fixture
def contest_spec_builder(recruiter_auth_manager: AuthManager) -> ContestSpecBuilder:
    return ContestSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def contest_response_handler(contest_spec_builder: ContestSpecBuilder) -> ContestResponseHandler:
    return ContestResponseHandler(contest_spec_builder)
