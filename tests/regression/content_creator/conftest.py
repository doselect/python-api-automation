"""Content-creator fixtures: creator-authenticated response handler and a shared, freshly created SCR problem."""
from __future__ import annotations

import pytest
import requests

from src.core.auth_manager import AuthManager
from src.core.do_api_config import CREATOR_EMAIL, CREATOR_PASSWORD, CREATOR_USERNAME
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler
from src.specs.content_creator_spec_builder import ContentCreatorSpecBuilder


def _creator_response_handler() -> ContentCreatorResponseHandler:
    # The creator session is also passed as the reviewer session: only the moderation specs use the
    # reviewer one, and the creator-only tests built on these fixtures never call them.
    creator_auth = AuthManager(CREATOR_EMAIL, CREATOR_PASSWORD)
    creator_auth.authenticate()
    return ContentCreatorResponseHandler(ContentCreatorSpecBuilder(creator_auth, creator_auth))


@pytest.fixture
def creator_response_handler() -> ContentCreatorResponseHandler:
    return _creator_response_handler()


@pytest.fixture(scope="module")
def scr_problem_create_response() -> requests.Response:
    """Creates one scripting (SCR) problem per module, shared by its read-only problem-page tests."""
    return _creator_response_handler().post_create_scr_problem(CREATOR_USERNAME)


@pytest.fixture
def scr_problem_slug(scr_problem_create_response: requests.Response) -> str:
    return scr_problem_create_response.json()["slug"]
