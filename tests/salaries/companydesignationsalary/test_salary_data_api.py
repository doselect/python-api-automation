"""
Mirrors tests.salaries.companydesignationsalary.SalaryDataAPITest (Java) — assertion-only tests
for the Salary Data API: GET /company/{companyId}/jobProfile/{jobProfileId}/salaryData.

Out of scope for this port (see python-api-automation/README.md):
- validateJobProfileGenericInProfileInfo (Metabase-driven random sampling)
- verifyMinMaxAvgCtcFromSalaryDataApi and the full offline-regression verifier logic
  (SalaryDataMinMaxAvgVerifier.verifyMinMaxAvgCtcWithOptionalOffline / SalaryDataComputationLogic)
- validateAverageCtcInBetweenTypicalMinMaxCtcInSummaryDataSection /
  ...InProfileInsightDataSection (both parametrized from sampledSalaries.csv, which is not part
  of this port's copied test data)
- negativeLocationId / incorrectLocationId (not listed in this port's required assertion set)

Deliberate deviation: the ported "min/max/avg CTC sanity check" test below uses a single
representative (companyId, jobProfileId) pair rather than parametrizing over sampledSalaries.csv,
since that CSV is out of scope and was not copied into this project.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from src.helpers.salaries.verifier.salary_data_min_max_avg_verifier import verify_min_max_avg_ctc
from src.reports.report_utils import log_test_summary
from src.responses.salaries_response_handler import SalariesResponseHandler

_TESTS_ROOT = Path(__file__).resolve().parents[2]  # python-api-automation/tests
_CSV_PATH = _TESTS_ROOT / "data" / "salaries" / "common_salaries.csv"
_SCHEMA_PATH = (
    _TESTS_ROOT / "schema" / "salaries" / "company_designation_salary_page" / "salary_data_api" / "schema.json"
)


def _load_common_salaries() -> list[tuple[int, int]]:
    """
    Mirrors @CsvFileSource(resources = "/data/salaries/commonSalaries.csv", numLinesToSkip = 1).

    The copied CSV's data rows use tab-padded commas (e.g. "42\\t,\\t10121"); int() strips that
    leading/trailing whitespace on its own, so no delimiter/whitespace adjustment to the file was
    needed to make it valid input for Python's csv module.
    """
    with _CSV_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return [(int(row[0]), int(row[1])) for row in rows[1:]]  # numLinesToSkip = 1


def _load_schema() -> dict[str, Any]:
    with _SCHEMA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


_COMMON_SALARIES = _load_common_salaries()
_SCHEMA = _load_schema()


@pytest.mark.parametrize("company_id, job_profile_id", _COMMON_SALARIES)
def test_happy_path_salary_data(
    salaries_response_handler: SalariesResponseHandler, company_id: int, job_profile_id: int
) -> None:
    """
    Mirrors happyPathSalaryData: every (companyId, jobProfileId) pair in commonSalaries.csv must
    return HTTP 200 with a body matching the Salary Data API JSON schema.
    """
    response = salaries_response_handler.get_cxd_salary_data(company_id, job_profile_id, {"locationId": 4})

    assert response.status_code == 200, "Expected status code 200 for valid companyId and jobProfileId"
    jsonschema.validate(instance=response.json(), schema=_SCHEMA)

    log_test_summary(
        "Salary Data API - Happy Path",
        [
            {
                "input": f"companyId={company_id}, jobProfileId={job_profile_id}",
                "expected_status": 200,
                "actual_status": response.status_code,
                "field_check": "schema valid",
                "result": "PASS",
            }
        ],
    )


def test_incorrect_company_id(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Mirrors incorrectCompanyId: an unknown/incorrect companyId still returns HTTP 200 (the API
    does not error on a company id that simply has no matching data).
    """
    response = salaries_response_handler.get_cxd_salary_data(400, 4, {"locationId": 4})

    assert response.status_code == 200, "Expected status code 200 for incorrect companyId"

    log_test_summary(
        "Salary Data API - Incorrect CompanyId",
        [
            {
                "input": "companyId=400, jobProfileId=4",
                "expected_status": 200,
                "actual_status": response.status_code,
                "field_check": "N/A",
                "result": "PASS",
            }
        ],
    )


def test_incorrect_job_profile_id(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Mirrors incorrectJobProfileId: an unknown/incorrect jobProfileId still returns HTTP 200.
    """
    response = salaries_response_handler.get_cxd_salary_data(42, 400, {"locationId": 4})

    assert response.status_code == 200, "Expected status code 200 for incorrect jobProfileId"

    log_test_summary(
        "Salary Data API - Incorrect JobProfileId",
        [
            {
                "input": "companyId=42, jobProfileId=400",
                "expected_status": 200,
                "actual_status": response.status_code,
                "field_check": "N/A",
                "result": "PASS",
            }
        ],
    )


def test_negative_company_id(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Mirrors negativeCompanyId: a negative companyId is rejected with HTTP 400.
    """
    response = salaries_response_handler.get_cxd_salary_data(-42, 4, {"locationId": 4}, expected_status_code=400)

    assert response.status_code == 400, "Expected status code 400 for negative companyId"

    log_test_summary(
        "Salary Data API - Negative CompanyId",
        [
            {
                "input": "companyId=-42, jobProfileId=4",
                "expected_status": 400,
                "actual_status": response.status_code,
                "field_check": "N/A",
                "result": "PASS",
            }
        ],
    )


def test_negative_job_profile_id(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Mirrors negativeJobProfileId: a negative jobProfileId is rejected with HTTP 400.
    """
    response = salaries_response_handler.get_cxd_salary_data(42, -4, {"locationId": 4}, expected_status_code=400)

    assert response.status_code == 400, "Expected status code 400 for negative jobProfileId"

    log_test_summary(
        "Salary Data API - Negative JobProfileId",
        [
            {
                "input": "companyId=42, jobProfileId=-4",
                "expected_status": 400,
                "actual_status": response.status_code,
                "field_check": "N/A",
                "result": "PASS",
            }
        ],
    )


def test_validate_response_time(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Mirrors validateResponseTime: the Salary Data API must respond in under 600ms for a
    known-good (companyId=42, jobProfileId=21) pair.
    """
    response = salaries_response_handler.get_cxd_salary_data(42, 21, {"locationId": 4})
    elapsed_ms = response.elapsed.total_seconds() * 1000

    assert response.status_code == 200, "Expected status code 200 for response time validation"
    assert elapsed_ms < 600, f"Expected response time < 600ms, got {elapsed_ms:.1f}ms"

    log_test_summary(
        "Salary Data API - Response Time",
        [
            {
                "input": "companyId=42, jobProfileId=21",
                "expected_status": 200,
                "actual_status": response.status_code,
                "field_check": f"responseTime={elapsed_ms:.1f}ms < 600ms",
                "result": "PASS",
            }
        ],
    )


@pytest.mark.parametrize("company_id, job_profile_id", _COMMON_SALARIES)
def test_validate_cache_control_header(
    salaries_response_handler: SalariesResponseHandler, company_id: int, job_profile_id: int
) -> None:
    """
    Mirrors validateCacheControlHeader: the Cache-Control response header must contain "no-cache"
    for every pair in commonSalaries.csv.
    """
    response = salaries_response_handler.get_cxd_salary_data(company_id, job_profile_id, {"locationId": 4})

    assert response.status_code == 200, "Expected status code 200 for cache control header validation"
    cache_control = response.headers.get("Cache-Control", "")
    assert "no-cache" in cache_control, "Cache-Control header should contain 'no-cache'"

    log_test_summary(
        "Salary Data API - Cache-Control Header",
        [
            {
                "input": f"companyId={company_id}, jobProfileId={job_profile_id}",
                "expected_status": 200,
                "actual_status": response.status_code,
                "field_check": "Cache-Control contains 'no-cache'",
                "result": "PASS",
            }
        ],
    )


def test_verify_min_max_avg_ctc(salaries_response_handler: SalariesResponseHandler) -> None:
    """
    Ported from the simple sanity check in SalaryDataMinMaxAvgVerifier (see the rules doc's "Code
    Structure Snippets" section): typicalMinCtc <= totalSalaryAverage <= typicalMaxCtc in
    data.summaryData, using the plain (no query params) getSalaryData call.
    """
    verify_min_max_avg_ctc(salaries_response_handler, 42, 21)

    log_test_summary(
        "Salary Data API - Min/Avg/Max CTC Sanity Check",
        [
            {
                "input": "companyId=42, jobProfileId=21",
                "expected_status": 200,
                "actual_status": 200,
                "field_check": "typicalMinCtc <= totalSalaryAverage <= typicalMaxCtc",
                "result": "PASS",
            }
        ],
    )
