"""Content dashboard: removing an allowed programming language keeps that language's stub and sample solution."""
from __future__ import annotations

import pytest

from src.core.do_api_config import CREATOR_USERNAME
from src.helpers.content_creator.payloads import auto_stub_ai_up_payloads
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

PAYLOADS = auto_stub_ai_up_payloads()
ALLOWED_TECHNOLOGIES = PAYLOADS["settings"]["technologies"]
LANGUAGE = next(iter(PAYLOADS["sample_solution"]["sample_solutions"]))  # cpp: has a stub and a solution
LANGUAGE_URI = f"/api/v1/technology/{LANGUAGE}"
SOLUTION = PAYLOADS["sample_solution"]["sample_solutions"][LANGUAGE]


def _assert_stub_and_solution_kept(problem: dict) -> None:
    assert problem["stubs"][LANGUAGE]["stub_type"] == "Auto-Generated"
    assert problem["stubs"][LANGUAGE]["code"] == PAYLOADS["auto_stubs"]["stubs"][LANGUAGE]["code"]
    assert problem["sample_solutions"][LANGUAGE]["solution"] == SOLUTION["solution"]
    assert problem["sample_solutions"][LANGUAGE]["solution_type"] == SOLUTION["solution_type"]


@pytest.mark.regression
def test_removed_language_keeps_stub_and_solution(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    handler, slug, rows = creator_response_handler, scr_problem_slug, []
    assert LANGUAGE_URI in ALLOWED_TECHNOLOGIES

    for step in ("settings", "auto_stubs", "sample_solution"):
        handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS[step])

    remaining = [uri for uri in ALLOWED_TECHNOLOGIES if uri != LANGUAGE_URI]
    response = handler.patch_problem(slug, CREATOR_USERNAME, {"technologies": remaining})
    assert LANGUAGE_URI not in response.json()["technologies"]
    _assert_stub_and_solution_kept(response.json())
    rows.append(summary_row(f"remove {LANGUAGE}", 202, response, "stub + solution kept"))

    response = handler.get_problem(slug, CREATOR_USERNAME)
    assert LANGUAGE_URI not in response.json()["technologies"]
    _assert_stub_and_solution_kept(response.json())
    rows.append(summary_row("reload", 200, response, "still removed, stub + solution kept"))

    log_test_summary("Content Creator - Remove Allowed Language Keeps Stub + Solution", rows)
