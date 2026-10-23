"""
Content dashboard: V2 problem with only Manual languages (Assembler, Bash, Clojure, Swift, Rust — no auto-generation).
Stubs are Default; editing one makes it User-Modified and reset brings it back to Default; a hand-written Assembler
solution passes the sanity check and the problem publishes. No AI generation is involved.
"""
from __future__ import annotations

import pytest

from src.core.do_api_config import CREATOR_USERNAME
from src.helpers.content_creator.auto_stub_flow import add_testcases_and_pass_sanity_check, publish
from src.helpers.content_creator.payloads import allowed_languages, manual_language_payloads, source_language
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

PAYLOADS = manual_language_payloads()
ALLOWED_LANGUAGES = allowed_languages(PAYLOADS)
SOLUTION_LANGUAGE = source_language(PAYLOADS)  # mars-assembler32: the only language with a sample solution
EDITED_STUB = SOLUTION_LANGUAGE
# Sanity checks run only for allowed languages that have a sample solution.
SANITY_LANGUAGES = ALLOWED_LANGUAGES & {SOLUTION_LANGUAGE}


def _stub_labels(problem: dict) -> dict[str, str]:
    return {language: stub["stub_type"] for language, stub in problem["stubs"].items()}


def _assert_edited_stub(problem: dict) -> None:
    """Every allowed language has a stub; only the edited one is User-Modified, the rest stay Default."""
    assert _stub_labels(problem) == {
        language: "User-Modified" if language == EDITED_STUB else "Default" for language in ALLOWED_LANGUAGES
    }
    assert problem["code_stub_generator"]["modified_stubs"] == [EDITED_STUB]
    assert problem["code_stub_generator"]["data"] == {}  # Manual languages: nothing is auto-generated
    assert problem["code_stub_generator"]["languages"] == []


@pytest.mark.regression
def test_manual_language_stubs_solution_sanity_and_publish(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    handler, slug, rows = creator_response_handler, scr_problem_slug, []

    def save(step: str) -> dict:
        response = handler.patch_problem(slug, CREATOR_USERNAME, PAYLOADS[step])
        rows.append(summary_row(step, 202, response, "saved"))
        return response.json()

    save("description")
    problem = save("settings")
    assert problem["problem_verification_status"] == "Verified"
    assert problem["verification_method"] == "Manual"

    _assert_edited_stub(save("edited_stubs"))

    problem = save("default_stubs")  # reset the edited stub
    assert set(_stub_labels(problem).values()) == {"Default"}
    assert problem["code_stub_generator"]["modified_stubs"] == []

    _assert_edited_stub(save("edited_stubs"))  # edit it again

    problem = save("sample_solution")
    assert problem["sample_solutions"][SOLUTION_LANGUAGE]["solution_type"] == "User-Modified"
    assert problem["sample_solutions_technologies"] == [f"/api/v1/technology/{SOLUTION_LANGUAGE}"]

    response = add_testcases_and_pass_sanity_check(
        handler, slug, CREATOR_USERNAME, payloads=PAYLOADS, sanity_languages=SANITY_LANGUAGES,
    )
    rows.append(summary_row("testcases + sanity check", 201, response, f"SUC, {SOLUTION_LANGUAGE} passed"))

    response = publish(handler, slug, CREATOR_USERNAME)
    rows.append(summary_row("publish", 202, response, "status PUB"))

    response = handler.get_problem(slug, CREATOR_USERNAME)
    problem = response.json()
    assert problem["status"] == "PUB"
    assert problem["is_active"] is True
    _assert_edited_stub(problem)
    assert problem["sample_solutions"][SOLUTION_LANGUAGE]["solution_type"] == "User-Modified"
    assert problem["sample_solutions"][SOLUTION_LANGUAGE]["sanity_status"] == "verified"
    assert problem["scr_solution_status"] is None  # no AI generation for Manual languages
    rows.append(summary_row("GET problem", 200, response, "published, labels kept, solution verified"))

    log_test_summary("Content Creator - Manual Language Stubs + Solution, Sanity Pass, Publish", rows)
