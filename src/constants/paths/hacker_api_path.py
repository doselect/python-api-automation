"""
Ports the endpoints exercised under tests/regression_api_methods/hacker/ +
tests/test_regression/test_hacker/ in https://github.com/doselect/do-api-automation.git.

Two base URLs are used (see the source files): most endpoints hit `DOSELECT_PRIMARY_DOMAIN` (same
host AuthManager/the test-gateway cookie flow live on); the Socket.IO long-polling handshake
(connect_websocket.py's three calls) hits `WEBSOCKET_DOMAIN` instead. `DO_TEST_INTERFACE_DOMAIN`
is never a base URL here — the source only ever uses it as the `origin`/`referer` header value
(see src/specs/session_auth_headers.py::default_hacker_headers).
"""
from __future__ import annotations

from src.core.do_api_config import DOSELECT_PRIMARY_DOMAIN, WEBSOCKET_DOMAIN

# gateways/test — GET (get_test_gateway.py), POST form submit x2 (post_test_gateway.py,
# post_test_gateway_submit.py) all hit the same path.
TEST_GATEWAY = "/gateways/test"

IDENTITY_GATEWAY = "/gateways/identity"
HACKER_DETAIL = "/api/v1/hacker/{hackerId}"
INFRA_ALLOCATE = "/rpc/infra/allocate/{solutionsetId}"
SECTIONWISE_PROBLEMS = "/api.v2/assessment/{testId}/sectionwise/problems"
ASSESSMENT_PROBLEMS = "/api.v2/assessment/{testId}/problems"
SERVER_TIME = "/rpc/get_server_time"
TECHNOLOGIES = "/rpc/get_technologies"
SOLUTION_LIST = "/api/v1/solution"
SOLUTION_DETAIL = "/api/v1/solution/{solutionSlug}"
CODE_RUN = "/rpc/code.run"
TEST_INIT = "/rpc/test.init/{testId}"
TEST_START = "/rpc/test.start/{testId}"
TEST_SUBMIT_ALL = "/rpc/test.submit_all/{solutionsetId}"
SOLUTIONS_SUBMIT = "/rpc/solutions.submit"
TEST_DETAIL = "/api/v1/test/{testSlug}"

# Socket.IO long-polling handshake (WEBSOCKET_DOMAIN base) — see connect_websocket.py.
SOCKET_IO = "/socket.io/"


def set_base_url() -> str:
    """Mirrors utils.config.DOSELECT_PRIMARY_DOMAIN (env var `DOSELECT_PRIMARY_DOMAIN`)."""
    return DOSELECT_PRIMARY_DOMAIN


def set_websocket_base_url() -> str:
    """Mirrors utils.config.WEBSOCKET_DOMAIN (env var `WEBSOCKET_DOMAIN`)."""
    return WEBSOCKET_DOMAIN
