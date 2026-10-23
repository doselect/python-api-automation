"""Content dashboard: auto-generated code stub problem flow while the AI solution service is down."""
from __future__ import annotations

import pytest

from src.core.do_api_config import AI_SOLUTION_SERVICE, CREATOR_USERNAME
from src.helpers.content_creator.payloads import auto_stub_problem_payloads
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

PAYLOADS = auto_stub_problem_payloads()
AI_SERVICE_DOWN_MESSAGE = "Upstream service timed out. Please try again"


def _check_description(problem: dict) -> None:
    assert problem["description"] == PAYLOADS["description"]["description"]


def _check_technologies(problem: dict) -> None:
    sent = PAYLOADS["technologies"]
    assert sorted(problem["technologies"]) == sorted(sent["technologies"])
    assert problem["solving_time"] == sent["solving_time"]


def _check_tags(problem: dict) -> None:
    sent = PAYLOADS["tags"]
    assert sorted(problem["tags"]) == sorted(sent["tags"])
    assert problem["insight_tags"] == sent["insight_tags"]
    assert problem["problem_verification_status"] == "Verified"
    assert problem["verification_method"] == "Manual"
    assert problem["verified_at"]


def _check_auto_stubs(problem: dict) -> None:
    sent = PAYLOADS["auto_stubs"]
    assert problem["extra_data"]["code_stub_type"] == "Auto-Generated"
    assert problem["code_stub_generator"]["data"] == sent["code_stub_generator"]["data"]
    assert problem["code_stub_generator"]["languages"] == sent["code_stub_generator"]["languages"]
    assert problem["stubs"] == sent["stubs"]


def _check_sample_solution(problem: dict) -> None:
    sent = PAYLOADS["sample_solution"]["sample_solutions"]["cpp14"]
    saved = problem["sample_solutions"]["cpp14"]
    assert saved["solution"] == sent["solution"]
    assert saved["solution_type"] == sent["solution_type"]
    assert saved["sanity_status"] == "not_verified"
    assert "/api/v1/technology/cpp14" in problem["sample_solutions_technologies"]


# Step name (= PAYLOADS key) -> (check, what the check covers). Runs in this order, like the dashboard.
STEPS = {
    "description": (_check_description, "description saved"),
    "technologies": (_check_technologies, "technologies + solving_time saved"),
    "tags": (_check_tags, "tags saved, problem marked Verified (Manual)"),
    "auto_stubs": (_check_auto_stubs, "Auto-Generated stubs saved for every language"),
    "sample_solution": (_check_sample_solution, "cpp14 solution saved, sanity_status=not_verified"),
}


@pytest.mark.regression
def test_auto_stub_problem_flow(creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str):
    """Each step is checked on its PATCH response, then all of them again on a fresh GET (persisted)."""
    rows = []
    for step, (check, field_check) in STEPS.items():
        response = creator_response_handler.patch_problem(scr_problem_slug, CREATOR_USERNAME, PAYLOADS[step])
        check(response.json())
        rows.append(summary_row(step, 202, response, field_check))

    response = creator_response_handler.get_problem(scr_problem_slug, CREATOR_USERNAME)
    for check, _ in STEPS.values():
        check(response.json())
    rows.append(summary_row("GET problem", 200, response, "all steps persisted"))

    log_test_summary("Content Creator - Auto Stub Problem Flow", rows)


@pytest.mark.regression
@pytest.mark.skipif(AI_SOLUTION_SERVICE != "down", reason="Needs the AI service down: run with AI_SOLUTION_SERVICE=down")
def test_generate_solution_ai_down(creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str):
    """
    The AI solution service is intentionally down on the test environment, so generating solutions for an
    auto-stub problem must fail with 502 and the upstream-timeout message. Fails once the service is back up.
    Stubs and a sample solution are saved first: without a sample solution the API returns 400
    NO_SOURCE_SOLUTION before it ever reaches the AI service.
    """
    for step in ("auto_stubs", "sample_solution"):
        creator_response_handler.patch_problem(scr_problem_slug, CREATOR_USERNAME, PAYLOADS[step])
    languages = PAYLOADS["generate_solution"]["languages"]

    response = creator_response_handler.post_generate_solution(
        scr_problem_slug, CREATOR_USERNAME, languages, expected_status_code=502,
    )
    body = response.json()

    assert body["status"] == "ERROR"
    assert body["description"] == AI_SERVICE_DOWN_MESSAGE

    log_test_summary("Content Creator - Generate Solution (AI service down)", [summary_row(
        f"languages={languages}", 502, response, f"status=ERROR, description='{AI_SERVICE_DOWN_MESSAGE}'",
    )])
