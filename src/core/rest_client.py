"""
Mirrors testutils.core.RestClient (Java) — GET-only subset needed for the ported Salary Data API
(no POST/PUT/DELETE/PATCH methods, since the Salary GET endpoint is all that's in scope here).

`execute_request` below is an additional, method-agnostic entry point added for the
do-api-automation port (https://github.com/doselect/do-api-automation.git), whose endpoints span
GET/POST/PATCH/PUT/DELETE — mirrors utils.api_helper.make_request's request/response shape (JSON
body in, `requests.Response` out) while staying on this module's RequestSpec-based calling
convention. It is additive: the GET-only functions above are untouched and still back the Salary
Data API port.
"""
from __future__ import annotations

import json as json_module
from typing import Any, Optional

import allure
import requests

from src.core.base_spec_builder import RequestSpec


def _resolve_url(spec: RequestSpec, path_params: Optional[dict[str, Any]]) -> str:
    """Substitutes {pathParam}-style placeholders in base_path, mirroring RestAssured path-param binding."""
    path = spec.base_path
    merged_path_params: dict[str, Any] = {**(spec.path_params or {}), **(path_params or {})}
    for key, value in merged_path_params.items():
        path = path.replace("{" + key + "}", str(value))
    return spec.base_url.rstrip("/") + path


def _merged_query_params(spec: RequestSpec, query_params: Optional[dict[str, Any]]) -> dict[str, Any]:
    merged = dict(spec.query_params or {})
    if query_params:
        merged.update(query_params)
    return merged


def execute_get_request(
    spec: RequestSpec,
    query_params: Optional[dict[str, Any]] = None,
    path_params: Optional[dict[str, Any]] = None,
    expected_status_code: int = 200,
) -> requests.Response:
    """
    Mirrors RestClient.executeGetRequest(spec, queryParams, pathParams[, expectedStatusCode]):
    executes a GET and asserts the response status code, raising AssertionError on mismatch
    (default expected status is 200, matching the Java overload).
    """
    url = _resolve_url(spec, path_params)
    response = requests.get(
        url,
        params=_merged_query_params(spec, query_params),
        headers=spec.headers,
        timeout=spec.timeout_ms / 1000,
    )
    if response.status_code != expected_status_code:
        raise AssertionError(
            f"Expected status code {expected_status_code} but got {response.status_code} "
            f"for GET {url} (body: {response.text[:500]!r})"
        )
    return response


def execute_get_request_without_status_assertion(
    spec: RequestSpec,
    query_params: Optional[dict[str, Any]] = None,
    path_params: Optional[dict[str, Any]] = None,
) -> requests.Response:
    """
    Mirrors RestClient.executeGetRequestWithoutStatusAssertion(...): executes a GET without
    asserting the status code — the caller is responsible for asserting it.
    """
    url = _resolve_url(spec, path_params)
    return requests.get(
        url,
        params=_merged_query_params(spec, query_params),
        headers=spec.headers,
        timeout=spec.timeout_ms / 1000,
    )


def execute_request(
    spec: RequestSpec,
    method: str,
    query_params: Optional[dict[str, Any]] = None,
    path_params: Optional[dict[str, Any]] = None,
    body: Optional[Any] = None,
    expected_status_code: Optional[int] = None,
) -> requests.Response:
    """
    Method-agnostic counterpart to execute_get_request, added for the do-api-automation port —
    mirrors utils.api_helper.make_request(endpoint, method, payload, headers) for GET/POST/PATCH/
    PUT/DELETE. `body` falls back to `spec.body` when omitted (matching how a spec-builder can
    carry a default payload). Status is asserted only when `expected_status_code` is given, so
    callers needing an unasserted call can omit it (mirrors the *_without_status_assertion methods
    above).
    """
    url = _resolve_url(spec, path_params)
    effective_body = body if body is not None else spec.body
    allure.attach(
        f"URL: {url}\nMethod: {method}\nHeaders: {json_module.dumps(spec.headers, indent=2)}\n"
        f"Payload: {json_module.dumps(effective_body, indent=2) if effective_body else 'None'}",
        name="API Request",
        attachment_type=allure.attachment_type.TEXT,
    )
    response = requests.request(
        method,
        url,
        params=_merged_query_params(spec, query_params),
        json=effective_body,
        headers=spec.headers,
        timeout=spec.timeout_ms / 1000,
    )
    allure.attach(
        f"Status Code: {response.status_code}\nResponse: {response.text}",
        name="API Response",
        attachment_type=allure.attachment_type.TEXT,
    )
    if expected_status_code is not None and response.status_code != expected_status_code:
        raise AssertionError(
            f"Expected status code {expected_status_code} but got {response.status_code} "
            f"for {method} {url} (body: {response.text[:500]!r})"
        )
    return response
