"""
Mirrors helpers.salaries.verifier.SalaryDataMinMaxAvgVerifier (Java) — only the simple sanity
check (min <= avg <= max) shown in the "Code Structure Snippets" section of
.agent/rules/serenity-api-automation-rules.md is ported. The full 497-line offline-regression
verifier logic (SalaryDataComputationLogic, OfflineSalaryDataFetcher, VerifierOptions, etc.) is
explicitly out of scope for this port — see python-api-automation/README.md.
"""
from __future__ import annotations

from src.models.salaries.salary_data_summary_response import SalaryDataSummaryResponse
from src.responses.salaries_response_handler import SalariesResponseHandler


def verify_min_max_avg_ctc(handler: SalariesResponseHandler, company_id: int, job_profile_id: int) -> None:
    """
    Mirrors SalaryDataMinMaxAvgVerifier's simple check: fetches the Salary Data API response via
    getSalaryData, parses it into SalaryDataSummaryResponse, and asserts
    typicalMinCtc <= totalSalaryAverage <= typicalMaxCtc from data.summaryData.
    """
    response = handler.get_salary_data(company_id, job_profile_id)
    body = SalaryDataSummaryResponse.model_validate(response.json())

    assert body.data is not None, "data should be present"
    assert body.data.summary_data is not None, "data.summaryData should be present"

    summary = body.data.summary_data
    assert summary.typical_min_ctc is not None, "typicalMinCtc should be present"
    assert summary.typical_max_ctc is not None, "typicalMaxCtc should be present"
    assert summary.total_salary_average is not None, "totalSalaryAverage should be present"

    assert summary.typical_min_ctc <= summary.total_salary_average <= summary.typical_max_ctc, (
        "Expected typicalMinCtc <= totalSalaryAverage <= typicalMaxCtc, got "
        f"min={summary.typical_min_ctc}, avg={summary.total_salary_average}, max={summary.typical_max_ctc}"
    )
