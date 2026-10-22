"""Content dashboard: auto-stub problem with the AI solution service up — AI generation, sanity check pass, publish."""
from __future__ import annotations

import pytest

from src.core.do_api_config import AI_SOLUTION_SERVICE, CREATOR_USERNAME
from src.helpers.content_creator.auto_stub_flow import (
    PAYLOADS,
    SANITY_LANGUAGES,
    SOURCE_LANGUAGE,
    TESTCASE_COUNT,
    add_testcases_and_pass_sanity_check,
    assert_solution_labels,
    assert_stubs_auto_generated,
    generate_ai_solutions,
)
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

pytestmark = pytest.mark.skipif(AI_SOLUTION_SERVICE == "down", reason="AI_SOLUTION_SERVICE=down: AI-up flow not runnable")


@pytest.mark.regression
def test_auto_stub_sanity_pass_and_publish(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    """
    Dashboard order: description -> settings (solving time, allowed languages, Verified tag) -> stubs ->
    hand-written cpp solution -> AI generates the rest -> testcases -> sanity check passes for every check -> publish.
    """
    handler, slug, rows = creator_response_handler, scr_problem_slug, []

    def save(step: str) -> dict:
        response = handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS[step])
        rows.append(summary_row(step, 202, response, "saved"))
        return response.json()

    save("description")
    problem = save("settings")
    assert problem["problem_verification_status"] == "Verified"
    assert problem["verification_method"] == "Manual"
    assert_stubs_auto_generated(save("auto_stubs"))
    assert save("sample_solution")["sample_solutions"][SOURCE_LANGUAGE]["solution_type"] == "User-Modified"

    response = generate_ai_solutions(handler, slug, CREATOR_USERNAME)
    rows.append(summary_row("generate_solution", 200, response, f"SUCCESS from {SOURCE_LANGUAGE}"))
    response = handler.get_problem(slug, CREATOR_USERNAME)
    assert_solution_labels(response.json())
    rows.append(summary_row("AI generated", 200, response, f"{SOURCE_LANGUAGE} User-Modified, rest Auto-Generated"))

    response = add_testcases_and_pass_sanity_check(handler, slug, CREATOR_USERNAME)
    rows.append(summary_row(
        "testcases + sanity check", 201, response,
        f"{TESTCASE_COUNT} testcases, SUC {len(SANITY_LANGUAGES)}/{len(SANITY_LANGUAGES)} passed",
    ))

    handler.patch_problem(slug, CREATOR_USERNAME, {"is_active": True})
    response = handler.post_set_problem_status_reviewer(slug)
    rows.append(summary_row("publish", 202, response, "status PUB"))

    response = handler.get_problem(slug, CREATOR_USERNAME)
    problem = response.json()
    assert problem["status"] == "PUB"
    assert problem["is_active"] is True
    assert_stubs_auto_generated(problem)
    assert_solution_labels(problem)
    for language in SANITY_LANGUAGES:
        assert problem["sample_solutions"][language]["sanity_status"] == "verified", language
    rows.append(summary_row("GET problem", 200, response, "published, labels kept, sanity-checked solutions verified"))

    log_test_summary("Content Creator - Auto Stub AI Up: Sanity Pass + Publish", rows)
