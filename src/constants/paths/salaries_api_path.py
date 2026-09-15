"""
Mirrors constants.paths.SalariesAPIPath (Java).

Only the SALARY_DATA path constant (and the base-URL resolvers it depends on) is ported here —
this first pass is scoped to the Salary Data API endpoint only (see python-api-automation/README.md
for the full out-of-scope list).
"""
from __future__ import annotations

from src.core.file_io_utils import get_property_value

# Real value copied from SalariesAPIPath.SALARY_DATA (Java).
SALARY_DATA = "/servicegateway-ambitionbox/salaries-services/v0/company/{companyId}/jobProfile/{jobProfileId}/salaryData"


def set_base_url() -> str:
    """Mirrors SalariesAPIPath.setBaseUrl(): reads BaseURL from config.properties."""
    return get_property_value("BaseURL")


def set_resdex_service_url() -> str:
    """
    Mirrors SalariesAPIPath.setResdexServiceUrl(): reads ResdexServiceURL from config.properties.
    Not used by the ported Salary Data API spec (which uses BaseURL); kept for parity with the
    Java constants class.
    """
    return get_property_value("ResdexServiceURL")
