"""
Shared fixtures for the ported do-api-automation `public_apis/*` domains — mirrors this repo's
root conftest.py convention (fresh spec-builder + response-handler per test).
"""
from __future__ import annotations

import pytest

from src.responses.fn_response_handler import FnResponseHandler
from src.responses.invite_response_handler import InviteResponseHandler
from src.responses.problems_response_handler import ProblemsResponseHandler
from src.specs.fn_spec_builder import FnSpecBuilder
from src.specs.invite_spec_builder import InviteSpecBuilder
from src.specs.problems_spec_builder import ProblemsSpecBuilder


@pytest.fixture
def problems_spec_builder() -> ProblemsSpecBuilder:
    builder = ProblemsSpecBuilder()
    builder.setup_all_specs()
    return builder


@pytest.fixture
def problems_response_handler(problems_spec_builder: ProblemsSpecBuilder) -> ProblemsResponseHandler:
    return ProblemsResponseHandler(problems_spec_builder)


@pytest.fixture
def invite_spec_builder() -> InviteSpecBuilder:
    builder = InviteSpecBuilder()
    builder.setup_all_specs()
    return builder


@pytest.fixture
def invite_response_handler(invite_spec_builder: InviteSpecBuilder) -> InviteResponseHandler:
    return InviteResponseHandler(invite_spec_builder)


@pytest.fixture
def fn_spec_builder() -> FnSpecBuilder:
    builder = FnSpecBuilder()
    builder.setup_all_specs()
    return builder


@pytest.fixture
def fn_response_handler(fn_spec_builder: FnSpecBuilder) -> FnResponseHandler:
    return FnResponseHandler(fn_spec_builder)
