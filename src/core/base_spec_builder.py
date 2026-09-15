"""
Mirrors src/test/java/specs/BaseSpecBuilder.java.

Provides a base request-spec container plus a builder function and the default-headers helper,
following the same defaults as the Java spec builder (20s timeout, AppId/SystemId + a generated
X-Transaction-Id on every request).
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Optional

from src.constants.headers.header_constants import HeaderConstants

# Mirrors BaseSpecBuilder.DEFAULT_TIMEOUT_MS (Java): default connection/socket (read) timeout in ms.
DEFAULT_TIMEOUT_MS = 20000


@dataclass
class RequestSpec:
    """Mirrors RestAssured's RequestSpecification as built by BaseSpecBuilder.buildRequestSpec(...)."""

    base_url: str
    base_path: str
    query_params: Optional[dict[str, Any]] = None
    headers: Optional[dict[str, str]] = None
    path_params: Optional[dict[str, Any]] = None
    body: Optional[Any] = None
    timeout_ms: int = DEFAULT_TIMEOUT_MS


def _generate_transaction_id() -> str:
    """Mirrors BaseSpecBuilder.generateTransactionId(): 20-char uppercase hex, no dashes."""
    return uuid.uuid4().hex[:20].upper()


def get_default_headers() -> dict[str, str]:
    """Mirrors BaseSpecBuilder.getDefaultHeaders(): AppId + SystemId + a fresh X-Transaction-Id."""
    headers = {
        HeaderConstants.APP_ID_KEY: HeaderConstants.APP_ID_VALUE,
        HeaderConstants.SYSTEM_ID_KEY: HeaderConstants.SYSTEM_ID_VALUE,
    }
    headers["X-Transaction-Id"] = _generate_transaction_id()
    return headers


def build_request_spec(
    base_url: str,
    base_path: str,
    query_params: Optional[dict[str, Any]] = None,
    headers: Optional[dict[str, str]] = None,
    path_params: Optional[dict[str, Any]] = None,
    body: Optional[Any] = None,
    timeout_ms: int = DEFAULT_TIMEOUT_MS,
) -> RequestSpec:
    """
    Mirrors BaseSpecBuilder.buildRequestSpec(...): bundles base URL/path, headers, query/path
    params, body and timeout into one reusable spec.
    """
    return RequestSpec(
        base_url=base_url,
        base_path=base_path,
        query_params=dict(query_params) if query_params else None,
        headers=dict(headers) if headers else None,
        path_params=dict(path_params) if path_params else None,
        body=body,
        timeout_ms=timeout_ms,
    )
