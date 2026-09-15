"""
Mirrors responses.SalariesResponseHandler (Java) — only the Salary Data API methods needed for
this port are included: getSalaryData / getCxdSalaryData and their status-assertion variants.
"""
from __future__ import annotations

from typing import Any, Optional

import requests

from src.core.rest_client import execute_get_request, execute_get_request_without_status_assertion
from src.specs.salaries_spec_builder import SalariesSpecBuilder


class SalariesResponseHandler:
    """Wraps a SalariesSpecBuilder to centralize Salary Data API calls."""

    def __init__(self, spec_builder: SalariesSpecBuilder) -> None:
        self._spec_builder = spec_builder

    def get_salary_data(self, company_id: int, job_profile_id: int) -> requests.Response:
        """
        Mirrors SalariesResponseHandler.getSalaryData(companyId, jobProfileId): path params only,
        asserts HTTP 200 (RestClient's default expected status).
        """
        path_params = {"companyId": company_id, "jobProfileId": job_profile_id}
        return execute_get_request(self._spec_builder.get_salary_data_spec(), None, path_params)

    def get_cxd_salary_data(
        self,
        company_id: int,
        job_profile_id: int,
        query_params: Optional[dict[str, Any]] = None,
        expected_status_code: int = 200,
    ) -> requests.Response:
        """
        Mirrors SalariesResponseHandler.getCxdSalaryData(companyId, jobProfileId, queryParams[,
        expectedStatusCode]).
        """
        path_params = {"companyId": company_id, "jobProfileId": job_profile_id}
        return execute_get_request(
            self._spec_builder.get_salary_data_spec(), query_params, path_params, expected_status_code
        )

    def get_cxd_salary_data_without_status_assertion(
        self,
        company_id: int,
        job_profile_id: int,
        query_params: Optional[dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Mirrors SalariesResponseHandler.getCxdSalaryDataWithoutStatusAssertion(companyId,
        jobProfileId, queryParams): no status assertion — the caller asserts.
        """
        path_params = {"companyId": company_id, "jobProfileId": job_profile_id}
        return execute_get_request_without_status_assertion(
            self._spec_builder.get_salary_data_spec(), query_params, path_params
        )
