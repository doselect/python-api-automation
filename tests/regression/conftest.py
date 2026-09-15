"""
Mirrors tests/test_regression/conftest.py (do-api-automation): failure-tracker DB init +
Teams-alert-on-session-finish hooks, the `--test-slug` CLI option, and a `shared_data` fixture.
Also provides `recruiter_auth_manager` — shared across all session-cookie-auth domains under
tests/regression/ (doiq, ai_interview, ...), since the source logs in as the recruiter the same
way (fresh `AuthManager(RECRUITER_EMAIL, RECRUITER_PASSWORD); .authenticate()`) in every one of
those test files.
"""
from __future__ import annotations

import pytest

from src.core.auth_manager import AuthManager
from src.core.do_api_config import RECRUITER_EMAIL, RECRUITER_PASSWORD
from src.core.failure_tracker import init_db, trigger_alert_on_failures
from src.responses.doiq_response_handler import DoiqResponseHandler
from src.specs.doiq_spec_builder import DoiqSpecBuilder

current_failures: set[str] = set()


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Initialize the database before tests start."""
    init_db()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect failed test case names but don't trigger alerts."""
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        current_failures.add(item.name)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """At the end of the test suite, trigger a single Teams alert if needed."""
    marker_expr = session.config.getoption("-m")
    if current_failures and "public" in marker_expr:
        trigger_alert_on_failures(current_failures)


def pytest_addoption(parser):
    parser.addoption(
        "--test-slug", action="store", default=None, help="Specify the test slug for the test run"
    )


@pytest.fixture(scope="function")
def shared_data() -> dict:
    return {}


@pytest.fixture
def recruiter_auth_manager() -> AuthManager:
    auth_manager = AuthManager(RECRUITER_EMAIL, RECRUITER_PASSWORD)
    auth_manager.authenticate()
    return auth_manager


@pytest.fixture
def doiq_spec_builder(recruiter_auth_manager: AuthManager) -> DoiqSpecBuilder:
    return DoiqSpecBuilder(recruiter_auth_manager)


@pytest.fixture
def doiq_response_handler(doiq_spec_builder: DoiqSpecBuilder) -> DoiqResponseHandler:
    return DoiqResponseHandler(doiq_spec_builder)
