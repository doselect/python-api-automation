"""
Mirrors constants.headers.HeaderConstants (Java).

The AppId/SystemId constants back BaseSpecBuilder.getDefaultHeaders() for the (no-auth) Salary
Data API. DOSELECT_API_KEY_HEADER/DOSELECT_API_SECRET_HEADER are an additive extension for the
do-api-automation port (https://github.com/doselect/do-api-automation.git) public APIs, which
authenticate via those two header names (see utils/config.py + inline headers dicts in that repo's
public_apis tests) rather than AppId/SystemId.
"""
from __future__ import annotations


class HeaderConstants:
    """Real values copied from constants.headers.HeaderConstants (Java)."""

    APP_ID_KEY = "AppId"
    SYSTEM_ID_KEY = "SystemId"
    APP_ID_VALUE = "125"
    SYSTEM_ID_VALUE = "Automation"

    # do-api-automation public APIs (DoSelect-Api-Key/Secret header auth).
    DOSELECT_API_KEY_HEADER = "DoSelect-Api-Key"
    DOSELECT_API_SECRET_HEADER = "DoSelect-Api-Secret"
