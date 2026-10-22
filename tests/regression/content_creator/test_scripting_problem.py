"""Content dashboard: scripting (SCR) problem creation, the APIs the creator problem page loads, creator stats and tag search."""
from __future__ import annotations

import pytest
import requests

from src.core.do_api_config import CREATOR_USERNAME
from src.reports.report_utils import log_test_summary, summary_row
from src.responses.content_creator_response_handler import ContentCreatorResponseHandler

VERIFIED_TAG = "Verified"


@pytest.mark.regression
def test_create_scripting_problem(scr_problem_create_response: requests.Response):
    body = scr_problem_create_response.json()

    assert scr_problem_create_response.headers.get("Location") == f"/api/v1/problem/{body['slug']}"
    assert body["name"].startswith("New-scr-problem-")
    assert body["problem_type"] == "SCR"
    assert body["eval_mode"] == "TXT"
    assert body["level"] == "MED"
    assert body["status"] == "DRA"
    assert body["scr_version"] == "V2"
    assert body["score"] == 100
    assert body["archived"] is False
    assert body["is_active"] is False
    assert body["creator"]["username"] == CREATOR_USERNAME

    log_test_summary("Content Creator - Create Scripting Problem", [summary_row(
        "problem_type=SCR, eval_mode=TXT, level=MED", 201, scr_problem_create_response,
        "Location, type/eval_mode/level, status=DRA, scr_version=V2, score=100, archived/is_active, creator",
    )])


@pytest.mark.regression
def test_get_scripting_problem_details(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_create_response: requests.Response,
    scr_problem_slug: str,
):
    response = creator_response_handler.get_problem(scr_problem_slug, CREATOR_USERNAME)
    body = response.json()

    assert response.headers.get("ETag")
    assert body["slug"] == scr_problem_slug
    assert body["name"] == scr_problem_create_response.json()["name"]
    assert body["problem_type"] == "SCR"

    log_test_summary("Content Creator - Get Scripting Problem Details", [summary_row(
        f"problem_slug={scr_problem_slug}", 200, response, "ETag present, slug/name/problem_type match created",
    )])


@pytest.mark.regression
@pytest.mark.parametrize("handler_method", ["get_problem_comments", "get_problem_testcases"])
def test_new_problem_has_no_comments_or_testcases(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str, handler_method: str
):
    response = getattr(creator_response_handler, handler_method)(scr_problem_slug, CREATOR_USERNAME)
    body = response.json()

    assert body["meta"]["total_count"] == 0
    assert body["objects"] == []

    log_test_summary(f"Content Creator - {handler_method}", [summary_row(
        f"problem_slug={scr_problem_slug}", 200, response, "meta.total_count == 0, objects == []",
    )])


@pytest.mark.regression
def test_solution_status_for_new_problem(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    response = creator_response_handler.get_solution_status(scr_problem_slug, CREATOR_USERNAME)
    body = response.json()

    assert body["status"] == "SUCCESS"
    assert body["problem_slug"] == scr_problem_slug
    assert body["scr_solution_status"] is None

    log_test_summary("Content Creator - Problem Solution Status", [summary_row(
        f"problem_slug={scr_problem_slug}", 200, response,
        "status=SUCCESS, problem_slug matches, scr_solution_status is None",
    )])


@pytest.mark.regression
def test_online_plagiarism_not_checked_for_new_problem(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    response = creator_response_handler.get_online_plagiarism_data(scr_problem_slug, CREATOR_USERNAME)
    body = response.json()

    assert body["description"] == "Not checked."
    assert body["status"] == "None"

    log_test_summary("Content Creator - Online Plagiarism Data", [summary_row(
        f"problem_slug={scr_problem_slug}", 200, response, "description='Not checked.', status='None'",
    )])


@pytest.mark.regression
def test_problem_check_not_found_for_new_problem(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    response = creator_response_handler.get_problem_check(scr_problem_slug, CREATOR_USERNAME)

    assert response.json() == {}

    log_test_summary("Content Creator - Problem Check (new problem)", [summary_row(
        f"problem_slug={scr_problem_slug}", 404, response, "body == {}",
    )])


@pytest.mark.regression
def test_code_stub_configuration_for_scr(
    creator_response_handler: ContentCreatorResponseHandler, scr_problem_slug: str
):
    response = creator_response_handler.get_code_stub_configuration(scr_problem_slug, "SCR")
    body = response.json()
    language_slugs = {language["slug"] for language in body["languages"]}

    assert body["problem_type"] == "SCR"
    assert {"python3", "java8", "cpp"} <= language_slugs
    assert body["return_types"]
    assert body["parameter_types"]

    log_test_summary("Content Creator - Code Stub Configuration", [summary_row(
        "problem_type=SCR", 200, response,
        "problem_type=SCR, languages include python3/java8/cpp, return_types/parameter_types non-empty",
    )])


@pytest.mark.regression
def test_creator_stats_distribution(creator_response_handler: ContentCreatorResponseHandler):
    response = creator_response_handler.get_creator_stats_getter(CREATOR_USERNAME)
    body = response.json()
    total = body["total_problems"]

    assert sum(item["value"] for item in body["status_distribution"]) == total
    assert sum(item["value"] for item in body["type_distribution"]) == total

    log_test_summary("Content Creator - Creator Stats", [summary_row(
        f"creator_username={CREATOR_USERNAME}", 200, response,
        f"status and type distributions each sum to total_problems ({total})",
    )])


@pytest.mark.regression
def test_tag_search(creator_response_handler: ContentCreatorResponseHandler):
    response = creator_response_handler.search_tags(VERIFIED_TAG)
    names = [tag["name"] for tag in response.json()["objects"][0]["objects"]]

    assert VERIFIED_TAG in names

    log_test_summary("Content Creator - Tag Search", [summary_row(
        f"q={VERIFIED_TAG}", 200, response, f"'{VERIFIED_TAG}' tag returned",
    )])
