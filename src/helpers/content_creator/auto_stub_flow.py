"""
Shared steps and checks of the auto-stub flows with the AI solution service up (AI generation, testcases, sanity
check), built on the auto_stub_ai_up.json data so every flow uses the same problem parameters.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

import requests

from src.helpers.content_creator.payloads import (
    ai_generation_languages,
    allowed_languages,
    auto_stub_ai_up_payloads,
    source_language,
)

if TYPE_CHECKING:
    from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

PAYLOADS = auto_stub_ai_up_payloads()
GENERATED_STUBS = PAYLOADS["auto_stubs"]
STUB_LANGUAGES = set(GENERATED_STUBS["code_stub_generator"]["languages"])
SOURCE_LANGUAGE = source_language(PAYLOADS)  # the hand-written solution (cpp)
GENERATED_LANGUAGES = ai_generation_languages(PAYLOADS)
# Sanity checks run only for allowed languages that have a sample solution.
SANITY_LANGUAGES = allowed_languages(PAYLOADS) & (GENERATED_LANGUAGES | {SOURCE_LANGUAGE})
TESTCASE_COUNT = len(PAYLOADS["testcases"])


def assert_stubs_auto_generated(problem: dict) -> None:
    assert set(problem["stubs"]) == STUB_LANGUAGES
    assert {stub["stub_type"] for stub in problem["stubs"].values()} == {"Auto-Generated"}


def assert_solution_labels(problem: dict) -> None:
    """The hand-written solution is User-Modified, every AI-generated one Auto-Generated."""
    solutions = problem["sample_solutions"]
    assert set(solutions) == GENERATED_LANGUAGES | {SOURCE_LANGUAGE}
    assert solutions[SOURCE_LANGUAGE]["solution_type"] == "User-Modified"
    for language in GENERATED_LANGUAGES:
        assert solutions[language]["solution_type"] == "Auto-Generated", language


def generate_ai_solutions(handler: ContentCreatorResponseHandler, slug: str, username: str) -> requests.Response:
    """Starts AI generation from the hand-written solution and waits until it reports Generated."""
    response = handler.post_generate_solution(slug, username, sorted(GENERATED_LANGUAGES), expected_status_code=200)
    body = response.json()
    assert body["status"] == "SUCCESS"
    assert body["scr_solution_status"] == "Generating"
    assert body["source_language"] == SOURCE_LANGUAGE
    assert set(body["target_languages"]) == GENERATED_LANGUAGES
    assert body["skipped_languages_missing_eligible_stub"] == []
    handler.wait_for_solution_generation(slug, username)
    return response


def add_testcases_and_pass_sanity_check(
    handler: ContentCreatorResponseHandler, slug: str, username: str,
    payloads: dict = PAYLOADS, sanity_languages: set[str] = SANITY_LANGUAGES,
) -> requests.Response:
    """
    Creates the `payloads` testcases, runs the sanity check and asserts that exactly `sanity_languages` were checked
    and every check passed all testcases. Defaults to the AI-up problem data.
    """
    testcase_count = len(payloads["testcases"])
    for testcase in payloads["testcases"]:
        handler.create_testcase(slug, username, testcase)
    assert handler.get_problem_testcases(slug, username).json()["meta"]["total_count"] == testcase_count

    response = handler.start_sanity_check(slug, username, payloads["sockmeta"])
    assert response.json()["uid"]
    check = handler.wait_for_sanity_check(slug, username)
    assert check["status"] == "SUC"
    assert set(check["results"]) == sanity_languages
    assert check["num_checks_total"] == check["num_checks_passed"] == len(sanity_languages)
    assert check["num_checks_failed"] == 0
    for language, result in check["results"].items():
        assert result["status"] == "ACC", language
        assert result["testcases_passed"] == result["testcases_total"] == testcase_count, language
    return response


def publish(handler: ContentCreatorResponseHandler, slug: str, username: str) -> requests.Response:
    """Makes the problem active, then publishes it (status PUB), as the dashboard's publish step does."""
    handler.patch_problem(slug, username, {"is_active": True})
    return handler.post_set_problem_status_reviewer(slug)
