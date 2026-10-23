"""
Content dashboard: stub and sample solution actions on an AI-up auto-stub problem (same parameters as the AI-up flow).
- Edit turns stubs / solutions User-Modified; reset brings back the generated Auto-Generated stubs (stubs only).
- Delete one / all stubs and solutions, re-create them, then testcases + sanity check still pass.
Every action is saved before the next one, as in the dashboard.
"""
from __future__ import annotations

import pytest

from src.core.do_api_config import AI_SOLUTION_SERVICE, CREATOR_USERNAME
from src.helpers.content_creator.auto_stub_flow import (
    GENERATED_STUBS,
    PAYLOADS,
    SANITY_LANGUAGES,
    SOURCE_LANGUAGE,
    add_testcases_and_pass_sanity_check,
    assert_solution_labels,
    assert_stubs_auto_generated,
    generate_ai_solutions,
)
from src.helpers.content_creator.payloads import (
    delete_all_stubs_payload,
    delete_solution_payload,
    delete_stub_payload,
    edited_solutions_payload,
    edited_stubs_payload,
    reset_stubs_payload,
)
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

pytestmark = pytest.mark.skipif(
    AI_SOLUTION_SERVICE == "down", reason="AI_SOLUTION_SERVICE=down: needs AI-generated solutions",
)

EDITED_STUBS = ["csharp", "cpp14"]  # same languages the dashboard recordings edited
EDITED_SOLUTION = "cpp14"           # an AI-generated (Auto-Generated) solution
DELETED_STUB = "csharp"             # same as the delete recording
DELETED_SOLUTION = "cpp14"          # same as the delete recording


def _stub_labels(problem: dict) -> dict[str, str]:
    return {language: stub["stub_type"] for language, stub in problem["stubs"].items()}


def _solution_labels(problem: dict) -> dict[str, str]:
    return {language: solution["solution_type"] for language, solution in problem["sample_solutions"].items()}


def _create_problem_with_ai_solutions(handler: ContentCreatorResponseHandler, slug: str) -> dict:
    """Settings -> generated stubs -> hand-written solution -> AI generates the rest. Returns the problem."""
    for step in ("settings", "auto_stubs", "sample_solution"):
        handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS[step])
    generate_ai_solutions(handler, slug, CREATOR_USERNAME)
    problem = handler.get_problem(slug, CREATOR_USERNAME).json()
    assert_stubs_auto_generated(problem)
    assert_solution_labels(problem)
    return problem


def _assert_reset(problem: dict) -> None:
    """Stubs are exactly the generated ones again; the edited sample solution keeps its User-Modified label."""
    assert problem["stubs"] == GENERATED_STUBS["stubs"]
    assert set(_stub_labels(problem).values()) == {"Auto-Generated"}
    assert problem["code_stub_generator"]["modified_stubs"] == []
    assert problem["sample_solutions"][EDITED_SOLUTION]["solution_type"] == "User-Modified"
    assert problem["sample_solutions"][SOURCE_LANGUAGE]["solution_type"] == "User-Modified"


@pytest.mark.regression
def test_edit_and_reset_stubs_and_solution(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    handler, slug, rows = creator_response_handler, scr_problem_slug, []
    solutions = _create_problem_with_ai_solutions(handler, slug)["sample_solutions"]
    assert solutions[EDITED_SOLUTION]["solution_type"] == "Auto-Generated"

    response = handler.patch_problem(slug, CREATOR_USERNAME, edited_stubs_payload(GENERATED_STUBS, EDITED_STUBS))
    problem = response.json()
    assert _stub_labels(problem) == {
        language: "User-Modified" if language in EDITED_STUBS else "Auto-Generated"
        for language in GENERATED_STUBS["stubs"]
    }
    assert sorted(problem["code_stub_generator"]["modified_stubs"]) == sorted(EDITED_STUBS)
    for language in EDITED_STUBS:
        assert problem["stubs"][language]["code"]["body"] != GENERATED_STUBS["stubs"][language]["code"]["body"]
    rows.append(summary_row(f"edit stubs {EDITED_STUBS}", 202, response, "Auto-Generated -> User-Modified"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, edited_solutions_payload(solutions, EDITED_SOLUTION))
    problem = response.json()
    assert problem["sample_solutions"][EDITED_SOLUTION]["solution_type"] == "User-Modified"
    assert problem["sample_solutions"][EDITED_SOLUTION]["solution"] != solutions[EDITED_SOLUTION]["solution"]
    for language, solution in solutions.items():
        if language != EDITED_SOLUTION:
            assert problem["sample_solutions"][language]["solution_type"] == solution["solution_type"], language
    rows.append(summary_row(f"edit solution {EDITED_SOLUTION}", 202, response, "Auto-Generated -> User-Modified"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, reset_stubs_payload(GENERATED_STUBS))
    _assert_reset(response.json())
    rows.append(summary_row("reset stubs", 202, response, "all stubs Auto-Generated, solutions untouched"))

    response = handler.get_problem(slug, CREATOR_USERNAME)
    _assert_reset(response.json())
    rows.append(summary_row("reload", 200, response, "reset persisted"))

    log_test_summary("Content Creator - Edit & Reset Stubs / Sample Solution", rows)


@pytest.mark.regression
def test_delete_and_recreate_stubs_and_solutions_then_sanity_pass(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    handler, slug, rows = creator_response_handler, scr_problem_slug, []
    problem = _create_problem_with_ai_solutions(handler, slug)
    labels_before = _solution_labels(problem)

    response = handler.patch_problem(slug, CREATOR_USERNAME, delete_stub_payload(GENERATED_STUBS, DELETED_STUB))
    problem = response.json()
    assert set(problem["stubs"]) == set(GENERATED_STUBS["stubs"]) - {DELETED_STUB}
    assert _solution_labels(problem) == labels_before  # deleting a stub never touches solutions
    rows.append(summary_row(f"delete stub {DELETED_STUB}", 202, response, "stub removed, solutions untouched"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, delete_all_stubs_payload(GENERATED_STUBS))
    problem = response.json()
    assert problem["stubs"] == {}
    assert "code_stub_type" not in problem["extra_data"]
    assert _solution_labels(problem) == labels_before
    rows.append(summary_row("delete all stubs", 202, response, "no stubs left, solutions untouched"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS["auto_stubs"])
    problem = response.json()
    assert_stubs_auto_generated(problem)
    assert problem["stubs"] == GENERATED_STUBS["stubs"]
    rows.append(summary_row("regenerate stubs", 202, response, "all stubs Auto-Generated again"))

    response = handler.patch_problem(
        slug, CREATOR_USERNAME, delete_solution_payload(problem["sample_solutions"], DELETED_SOLUTION),
    )
    problem = response.json()
    assert set(problem["sample_solutions"]) == set(labels_before) - {DELETED_SOLUTION}
    assert f"/api/v1/technology/{DELETED_SOLUTION}" not in problem["sample_solutions_technologies"]
    rows.append(summary_row(f"delete solution {DELETED_SOLUTION}", 202, response, "solution removed"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, {"sample_solutions": {}})
    problem = response.json()
    assert problem["sample_solutions"] == {}
    assert problem["sample_solutions_technologies"] == []
    assert problem["scr_solution_status"] is None  # AI generation status is cleared with the solutions
    assert_stubs_auto_generated(problem)             # stubs are kept
    rows.append(summary_row("delete all solutions", 202, response, "no solutions, AI status cleared, stubs kept"))

    response = handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS["sample_solution"])
    assert response.json()["sample_solutions"][SOURCE_LANGUAGE]["solution_type"] == "User-Modified"
    rows.append(summary_row(f"re-add solution {SOURCE_LANGUAGE}", 202, response, "User-Modified"))

    response = generate_ai_solutions(handler, slug, CREATOR_USERNAME)
    assert_solution_labels(handler.get_problem(slug, CREATOR_USERNAME).json())
    rows.append(summary_row("generate solutions again", 200, response, "rest Auto-Generated again"))

    response = add_testcases_and_pass_sanity_check(handler, slug, CREATOR_USERNAME)
    rows.append(summary_row(
        "testcases + sanity check", 201, response, f"SUC {len(SANITY_LANGUAGES)}/{len(SANITY_LANGUAGES)} passed",
    ))

    response = handler.get_problem(slug, CREATOR_USERNAME)
    problem = response.json()
    assert_stubs_auto_generated(problem)
    assert_solution_labels(problem)
    for language in SANITY_LANGUAGES:
        assert problem["sample_solutions"][language]["sanity_status"] == "verified", language
    rows.append(summary_row("reload", 200, response, "re-created stubs/solutions kept, checked solutions verified"))

    log_test_summary("Content Creator - Delete & Re-create Stubs / Solutions, Sanity Pass", rows)
