"""
Content dashboard: bulk MCQ upload from CSV — Draft uploads stay hidden from the DoSelect Library, Approved uploads
are published and visible in it; both come back AI-verified and matching the CSV.
"""
from __future__ import annotations

import pytest

from src.core.do_api_config import CREATOR_USERNAME
from src.helpers.content_creator.payloads import MCQ_BULK_CSV, mcq_bulk_rows
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

ALL_ROWS = mcq_bulk_rows()
CHECKED_ROWS = ALL_ROWS[:5]  # only the first five MCQs are verified in detail
LEVELS = {"easy": "EAS", "medium": "MED", "hard": "HAR"}
OPTION_COLUMNS = [f"Option {i}" for i in range(1, 11)]


def _split(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _assert_matches_csv(problem: dict, row: dict) -> None:
    correct = _split(row["Correct Answer"])
    assert problem["problem_type"] == "MCQ"
    assert problem["level"] == LEVELS[row["Level(mandatory)"].strip().lower()]
    assert problem["solving_time"] == row["Solving Time In Minutes(mandatory)"]
    assert problem["score"] == int(row["Score (optional)"])
    assert problem["penalty"] == int(row["Penalty (optional)"])
    assert set(_split(row["Tags (optional)"])) <= set(problem["tags"])
    assert problem["insight_tags"] == _split(row["Insight Tags (optional)"])
    assert problem["mcq_options_correct"] == correct
    assert problem["is_multi_correct"] == (len(correct) > 1)
    assert len(problem["mcq_options"]) == sum(1 for column in OPTION_COLUMNS if row[column].strip())


def _assert_ai_verified(problem: dict) -> None:
    assert problem["problem_verification_status"] == "Verified"
    assert problem["verification_method"] == "AiVerified"
    assert "Verified" in problem["tags"]


@pytest.mark.regression
@pytest.mark.parametrize(
    "mode, auto_approval, expected_status, expected_visibility",
    [
        # visibility: "MAR" = in the DoSelect Library, "PRI" = private to the company, [] = neither.
        ("Draft", False, "DRA", []),          # Draft ticked: not in the DoSelect Library
        ("Approved", True, "PUB", ["MAR"]),   # Draft unticked: published in the DoSelect Library
    ],
)
def test_mcq_bulk_upload(
    creator_response_handler: ContentCreatorResponseHandler, mode: str, auto_approval: bool,
    expected_status: str, expected_visibility: list[str],
):
    """
    Every upload creates new problems (new slugs). Only problems created by this upload are checked —
    matched on its evaluation job id — so same-named MCQs from earlier uploads are ignored.
    """
    handler, rows = creator_response_handler, []

    response = handler.upload_mcq_bulk_file(MCQ_BULK_CSV, CREATOR_USERNAME)
    body = response.json()
    assert body["status"] == "OK"
    assert body["description"] == f"{len(ALL_ROWS)} valid problems found."
    rows.append(summary_row(f"upload {MCQ_BULK_CSV.name}", 200, response, body["description"]))

    response = handler.confirm_mcq_bulk_upload(body["filename"], CREATOR_USERNAME, auto_approval=auto_approval)
    body = response.json()
    assert body["status"] == "OK"
    assert body["plagiarism_service_response"]["total_records"] == len(ALL_ROWS)
    job_id = body["evaluation_job_id"]
    rows.append(summary_row(f"confirm as {mode}", 200, response, f"job {job_id}"))

    problems = handler.wait_for_bulk_uploaded_problems(
        [row["Name (min 6 char)"] for row in CHECKED_ROWS], job_id, CREATOR_USERNAME,
    )
    for row in CHECKED_ROWS:
        problem = problems[row["Name (min 6 char)"]]
        _assert_matches_csv(problem, row)
        _assert_ai_verified(problem)
        assert problem["status"] == expected_status
        assert problem["visibility"] == expected_visibility
        rows.append({
            "input": problem["name"], "expected_status": expected_status, "actual_status": problem["status"],
            "field_check": (
                f"slug={problem['slug']} visibility={problem['visibility']} level={problem['level']} "
                f"verification={problem['problem_verification_status']}/{problem['verification_method']} "
                f"tags={problem['tags']} correct={problem['mcq_options_correct']}"
            ),
            "result": "PASS",
        })

    log_test_summary(f"Content Creator - MCQ Bulk Upload ({mode})", rows)
