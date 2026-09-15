"""
Mirrors pojos.salaries.SalaryDataSummaryResponse (Java).

Per the POJO Location Rule in the framework rules doc, this is a response model consumed only by
test/verifier code (never instantiated in a spec builder or response handler), so it lives under
src/models (the Python equivalent of src/test/java/pojos/<domain>/).
"""
from __future__ import annotations

from typing import Any, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class SummaryData(BaseModel):
    """Mirrors SalaryDataSummaryResponse.SummaryData (Java)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    # Java: @JsonAlias({"minCtc"}) on typicalMinCtc -> accept either JSON key.
    typical_min_ctc: Optional[float] = Field(
        default=None, validation_alias=AliasChoices("typicalMinCtc", "minCtc")
    )
    # Java: @JsonAlias({"maxCtc"}) on typicalMaxCtc -> accept either JSON key.
    typical_max_ctc: Optional[float] = Field(
        default=None, validation_alias=AliasChoices("typicalMaxCtc", "maxCtc")
    )
    total_salary_average: Optional[float] = Field(default=None, alias="totalSalaryAverage")
    total_salary_data_points: Optional[int] = Field(default=None, alias="totalSalaryDataPoints")


class DataNode(BaseModel):
    """Mirrors SalaryDataSummaryResponse.DataNode (Java)."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    summary_data: Optional[SummaryData] = Field(default=None, alias="summaryData")


class SalaryDataSummaryResponse(BaseModel):
    """Mirrors pojos.salaries.SalaryDataSummaryResponse (Java) — top-level response wrapper."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    meta: Optional[Any] = None
    data: Optional[DataNode] = None
