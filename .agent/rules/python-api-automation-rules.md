# Python API Automation Rules

## Purpose
Use these rules whenever creating or updating API automation in this repository
(`python-api-automation`) — a standalone pytest suite for DoSelect's Recruit / Interview /
Hacker / Contest / DOIQ / AI-Interview / Content-Creator / public APIs, built as a layered
spec-builder → response-handler → test framework. This file describes the suite as it actually
exists today, not an aspirational or translated structure — every convention below is backed by
real code in this repo.

## Core Principles
- Follow the conventions already established in this project.
- Keep code concise and non-verbose.
- Write maintainable and reusable test automation code.
- Add clear documentation (module-level and function-level docstrings where useful), but avoid
  unnecessary long comments.

## Change Guardrails (Mandatory)
- Always create an action plan before changing anything in the codebase.
- Share the plan with the user and wait for explicit approval before making code changes.
- Do not modify existing code structure unless asked.
- Do not remove or weaken existing assertions unless explicitly requested.
- Do not rearrange imports, utilities, or existing file organization unless explicitly requested.
- Do not perform refactors, formatting-only churn, or naming cleanups outside requested scope.
- Keep diffs minimal and task-focused.
- If scope is unclear, ask before editing.
- Preserve backward compatibility of existing tests unless the user asks for behavior change.

## Fact-Only Guardrails (Mandatory)
- Do not fabricate or assume assertions, API endpoints, URLs, credentials, tokens, headers,
  payload fields, expected status codes, or test data.
- Use only facts explicitly provided by the user or already present in the codebase (existing
  spec builders, response handlers, `src/core/do_api_config.py`, `pyproject.toml`, test data
  files).
- If any required detail is missing, pause and ask the user for the exact value, or leave a
  clearly marked `# TODO` comment — never guess a plausible-looking value.
- Do not infer secrets or environment-specific values. All credentials/URLs are environment
  variables read in `src/core/do_api_config.py` — never hardcode a real key/secret/email/password
  in source.
- Keep implementation strictly aligned with user-provided requirements and existing framework
  facts.

## Architecture (How A Request Flows)
Four layers, each with one job — never collapse them into the test function:

1. **`src/constants/paths/*_api_path.py`** — endpoint path constants + a `set_base_url()` (and,
   where a domain hits a second host, an additional resolver such as
   `recruit_api_path.set_dolores_base_url()`) that reads the relevant env var from
   `do_api_config.py`.
2. **`src/specs/*_spec_builder.py`** — builds `RequestSpec` objects (`src/core/
   base_spec_builder.py`'s `build_request_spec`/`RequestSpec`) that bundle base URL, base path,
   headers, and optional default query/path params/body. One class per domain
   (`RecruitSpecBuilder`, `ProblemsSpecBuilder`, ...). A spec builder never calls `requests`
   itself.
3. **`src/responses/*_response_handler.py`** — one method per API operation, each calling
   `src.core.rest_client.execute_request` (method-agnostic: GET/POST/PATCH/PUT/DELETE, optional
   `expected_status_code` assertion, Allure request/response attachment) or the GET-only
   `execute_get_request`/`execute_get_request_without_status_assertion`. Path/query params and
   body-building live here, not in the test.
4. **`tests/<public_apis|regression>/<domain>/test_*.py`** — assertion/scenario layer only:
   arrange test data → call the response handler → assert on the result. No `requests` calls, no
   header/URL construction, in a test file.

Supporting layers:
- **`src/helpers/<domain>/payloads.py`** — request-body builders (one function per payload
  shape), imported by the domain's response handler. `src/helpers/interview/email_otp.py` is the
  one example of a non-payload helper (wraps `src/core/email_reader.py`'s IMAP read).
- **`src/core/`** — shared infrastructure: `base_spec_builder.py` (RequestSpec/timeout/
  transaction-id), `rest_client.py` (HTTP execution + Allure attach), `auth_manager.py`
  (`AuthManager` session-cookie+CSRF login), `do_api_config.py` (env-var config + CSV test data),
  `do_api_helpers.py` (misc helpers, e.g. `retry_api_call`, `encode_url`), `do_api_logger.py`
  (logger setup), `response_validator.py` (`validate_response_code`/`validate_response_schema`),
  `failure_tracker.py` (SQLite flaky-failure counter + Teams alert), `email_reader.py` (real
  IMAP read).
- **`src/constants/headers/`** — `header_constants.py` (named header-key/value constants),
  `static_headers.py`, `browser_fingerprint_headers.py` (shared literal fingerprint header
  blocks, e.g. `CHROME_WINDOWS_FINGERPRINT_HEADERS`).
- **`src/specs/session_auth_headers.py`** — the *generic, role-based default* header shape
  (`default_recruiter_headers`, `default_hacker_headers`, `default_content_creator_headers`,
  `default_reviewer_headers`), each taking an `AuthManager` and an `only_auth` flag. Use these
  when a new endpoint's headers match one of these default shapes; build a literal dict in the
  domain's own spec builder when an endpoint needs something more specific (most do — see
  existing spec builders for the repeated shapes already factored out, e.g.
  `RecruitSpecBuilder._fingerprint_headers`/`_plain_recruit_headers`).
- **`src/reports/report_utils.py`** — `log_test_summary(title, rows)`, the Allure tabular-summary
  helper (see Reporting Rule below).

## Mandatory Flow For New API Tests
1. **Check existing implementation first**: search `src/specs`, `src/responses`, `src/helpers`,
   `src/constants`, and the relevant domain's existing tests/conftest before writing anything new.
   Reuse before creating.
2. **Path constants**: add the new endpoint's path to the domain's `*_api_path.py` if it isn't
   already there.
3. **Spec builder**: add a method (or a new literal header dict, matching the domain's existing
   style) to the domain's `*_spec_builder.py`. Never build a `RequestSpec` or a headers dict
   inline inside a response-handler method or a test.
4. **Response handler**: add a method to the domain's `*_response_handler.py` that calls
   `execute_request`/`execute_get_request`, with a docstring one-liner naming the HTTP
   method+path it hits. Keep `expected_status_code` as a parameter with a sensible default so
   callers can override it for negative-path tests.
5. **Test**: arrange data (fixtures, payload helpers, prior response-handler calls) → call the
   response handler → assert on the result. Prefer `pytest.mark.parametrize` for data-driven
   coverage.

## Auth Patterns (Mandatory — Ask Before Implementing If Unclear)
There are exactly two auth mechanisms in this repo. Before writing a new domain or endpoint, know
which one applies — check how sibling endpoints in the same domain authenticate rather than
guessing:

### Pattern 1 — API Key/Secret Header Auth (`public_apis/*`: `problems`, `invite`, `fn`)
- Stateless: every request carries `DoSelect-Api-Key`/`DoSelect-Api-Secret` headers
  (`HeaderConstants.DOSELECT_API_KEY_HEADER`/`DOSELECT_API_SECRET_HEADER`), values from
  `do_api_config.DOSELECT_API_KEY`/`DOSELECT_API_SECRET` (the `fn` domain uses its own
  `FN_API_KEY`/`FN_API_SECRET`/`FN_COMPANY_SLUG` — check the existing `FnSpecBuilder` before
  assuming the generic pair applies).
- Spec builder pattern: a module-level `get_<domain>_headers()` function returning the two-header
  dict, a spec-builder class with a `setup_all_specs()`/`_spec_for(key, base_path)` cache, and a
  `get_spec(key)` accessor (see `ProblemsSpecBuilder`).
- No `AuthManager`, no per-test login — fixtures in `tests/public_apis/conftest.py` just
  instantiate the spec builder and call `setup_all_specs()`.

### Pattern 2 — Session-Cookie + CSRF Auth (`regression/*`: `recruit`, `interview`, `hacker`,
`contest`, `doiq`, `ai_interview`, `content_creator`)
- `src/core/auth_manager.py::AuthManager(account_email, account_password)` scrapes the login
  page's `csrfmiddlewaretoken`, POSTs credentials, and reads the `sessionid` cookie. Call
  `.authenticate()` once (or let the lazy `.headers`/`.cookie`/`.csrf_token`/`.session_id`
  properties trigger it) — a fresh `AuthManager` is built per test (no cross-test session reuse),
  matching how every `regression/*` domain does it today.
- Role/account type comes from which credentials you pass in, not from an `AuthManager`
  parameter: `RECRUITER_EMAIL`/`RECRUITER_PASSWORD` for the recruiter role;
  `CREATOR_USERNAME`/`CREATOR_PASSWORD`, `REVIEWER_USERNAME`/`REVIEWER_PASSWORD`,
  `MODERATOR_USERNAME`/`MODERATOR_PASSWORD`, etc. for the others — all read from
  `do_api_config.py`. `USER_TYPE_RECRUITER`/`USER_TYPE_CANDIDATE`/`USER_TYPE_INTERVIEWER`/
  `USER_TYPE_CREATOR`/`USER_TYPE_REVIEWER` are the role-name constants used when picking a
  `session_auth_headers.default_*_headers` function, not arguments to `AuthManager` itself.
- The candidate/hacker side is the one exception: it never builds an `AuthManager` — it
  exchanges an access-code test-invite link for cookies via `/gateways/test` (see
  `hacker_spec_builder.py::CandidateSession`, a small object that duck-types
  `AuthManager.csrf_token`/`.cookie` so `default_hacker_headers` can be reused unmodified).
- Fixtures: a domain's `conftest.py` provides `<domain>_spec_builder`/`<domain>_response_handler`
  fixtures built on an `AuthManager` fixture (see `tests/regression/conftest.py`'s
  `recruiter_auth_manager`, shared across domains that log in as the recruiter). Add a new
  domain's fixtures to its own `tests/regression/<domain>/conftest.py` unless it genuinely reuses
  an existing shared fixture.

### Clarifying Questions Before Any New Auth Setup
If unsure which pattern or which role/credentials a new endpoint needs, ask:
1. Does this endpoint live under `public_apis/` (API key/secret) or `regression/` (session
   cookie)?
2. Which role logs into it — recruiter, hacker/candidate, interviewer, content creator, reviewer,
   moderator? Which `do_api_config.py` credential pair backs that role?
3. Does an existing `session_auth_headers.default_*_headers` shape fit, or does the endpoint need
   its own literal header dict (check the domain's sibling endpoints first)?

Do not guess an auth mechanism from the endpoint's name — verify against a sibling endpoint in
the same domain or ask the user.

## Config & Test Data
- All environment-specific values (`BASE_URL`, `DOSELECT_API_KEY`/`SECRET`, `RECRUITER_EMAIL`/
  `PASSWORD`, `DOSELECT_PRIMARY_DOMAIN`, etc.) are environment variables read once in
  `src/core/do_api_config.py`. Add a new config value there (as `os.environ.get("...")`) rather
  than reading `os.environ` directly elsewhere.
- Per-environment test data (slugs, IDs, usernames) lives in one CSV,
  `tests/data/do_api_automation/data.csv`, read via `do_api_config.get_csv_data(key,
  environment)`. Add new rows there rather than hardcoding a slug/ID in a test or payload helper.
- There is no `config.properties` file and no properties-file reader in this repo — don't
  introduce one.

## Response Validation
- `src/core/response_validator.py::validate_response_code(test_case_name, response,
  expected_status_code)` is the shared assertion helper — it also feeds `failure_tracker` (SQLite
  flaky-counter + Teams alert) when `ENVIRONMENT == "PRODUCTION"`. Prefer it over a bare
  `assert response.status_code == ...` when you want that tracking; a bare assert is fine for
  quick/negative-path checks that don't need tracking.
- Most existing response-handler methods already assert status via `execute_request`'s
  `expected_status_code` parameter — don't duplicate that assertion again in the test unless
  you're checking a *different* status than the handler's default (e.g. a negative-path test
  calling the handler with an overridden `expected_status_code`).
- `validate_response_schema(response, schema_file)` exists (reads from a `schemas/` directory)
  but no schema files exist in this repo yet and nothing calls it today. Only add
  `schemas/<file>.json` + a call to it if the task actually requires schema validation — don't
  invent a schema.

## Reporting Rule (Mandatory Going Forward)
`src/reports/report_utils.py::log_test_summary(title, rows)` attaches an aligned text table
(`input | expected_status | actual_status | field_check | result`) to the Allure report — Python's
equivalent of a structured per-test result summary.

- Call `log_test_summary(...)` at the end of every **new or updated** test function that is
  parametrized, or that validates specific response fields (not just a bare status-code check
  already covered by the response handler's `expected_status_code`).
- `rows` is a list of dicts, one per scenario/iteration, each with keys: `input`,
  `expected_status`, `actual_status`, `field_check`, `result`.
- Title must identify the scenario, e.g. `"Recruit - Get Company Details"`.
- If a test only checks status/schema (no business fields), still record input params + status +
  a `field_check` describing what was checked (e.g. `"schema valid"`, `"N/A"`).
- This is not yet followed by most of the existing suite (it predates this rule) — do not treat
  an untouched existing test's lack of a `log_test_summary` call as something to fix unless you
  are already changing that test for another reason.

## Test Case Design Rules (Mandatory)
- No TC IDs in test function names (no `_TC001`-style suffixes).
- Test files are **feature-based**, not endpoint-based: one file per feature/scenario under
  `tests/public_apis/<domain>/test_*.py` or `tests/regression/<domain>/test_*.py`. Don't split
  one feature's happy-path/negative-path scenarios across multiple files.
- Docstrings: every test module should keep a short one-line module docstring stating what it
  covers. Add a **function-level** docstring only when what the test validates isn't obvious from
  its name and body (non-obvious business rule, a documented source quirk being preserved, a
  workaround) — most existing tests are self-explanatory from their name + the response-handler
  call and don't need one; don't add boilerplate docstrings that just restate the function name.
- Each test function must assert something unique that no other test in the file covers; club
  scenarios to eliminate redundancy — don't add a standalone 200-status test if the response
  handler already asserts 200 via `expected_status_code` before the test can even proceed.
- Use `pytest.mark.skip(reason=...)` / `pytest.mark.xfail(reason=...)` with a clear explanatory
  message for tests that need external setup that isn't available (blocked accounts, missing
  second test users, infra/DB state). Never leave a skip/xfail with an empty or vague reason.
- Prefer `pytest.mark.parametrize`, optionally sourced from `do_api_config.get_csv_data(...)` or a
  small local list/CSV loader, for data-driven coverage.

## Pytest Markers (Mandatory)
- Every test carries at least its domain-group marker: `@pytest.mark.public` for
  `public_apis/*`, `@pytest.mark.regression` for `regression/*` (plus `@pytest.mark.hacker`/
  `smoke` where applicable, matching sibling tests in the same file/domain).
- All markers must be registered in `pyproject.toml`'s `[tool.pytest.ini_options].markers` list —
  add a new marker there in the same change that introduces it. Don't introduce an unregistered
  marker.
- Feature-specific markers (e.g. `add_criteria`, `clone_contest`) exist per scenario in some
  domains (see the `contest` markers) — follow that domain's existing convention if adding a
  sibling scenario; don't invent a new naming scheme for an existing domain.

## Parallel Execution (`pytest-xdist`) Rule
This suite runs with `pytest -n auto` (see `test.sh`/`Jenkinsfile`). Some tests share mutable
server-side state across workers and must not run concurrently with each other:
- `tests/regression/contest/*` — every test resolves "the contest to operate on" via a
  company-wide "most recent contest" GET, not one scoped to that test's own creation; concurrent
  workers race and mutate/supersede each other's contest.
- Any test that reads an OTP from a shared inbox (e.g. `AUTOMATION_EMAIL`) — concurrent workers
  can consume the OTP meant for a different worker.

`tests/regression/conftest.py::pytest_collection_modifyitems` tags matching tests with
`pytest.mark.xdist_group(name="...")` so `-n auto --dist=loadgroup` pins them to the same worker
without reducing parallelism elsewhere. If you add a new test that shares similar mutable,
non-test-scoped server state with other tests (a "most recent X" lookup, a shared mailbox, a
shared singleton record), add it to that same `pytest_collection_modifyitems` function under a
new or existing `xdist_group` — don't assume test isolation that the API doesn't actually
provide.

## Reusability Rules
- Before adding a new utility/helper module, search existing `src/helpers`, `src/core`,
  `src/specs`, and `src/constants` packages.
- If similar logic exists, extend/refactor that module instead of duplicating.
- New shared logic must go into a reusable module under `src/`, not copied across test files.
- Cross-domain reuse is expected and already happens (e.g. `ai_interview` reusing
  `doiq_response_handler` for shared `/doiq/*` calls, `recruit`/`hacker` sharing a spec/response
  handler pair for the hacker attempt-flow prerequisite) — prefer calling another domain's
  response handler over duplicating its logic when the underlying endpoint is genuinely shared.

## Code Quality Rules
- Avoid hardcoded values when constants/config already exist (`src/constants/...`,
  `do_api_config.py`, `tests/data/do_api_automation/data.csv`).
- Keep functions small and purpose-driven.
- Use meaningful names for test functions, data files, and helper functions.
- Prefer plain `assert` statements (pytest's assertion rewriting gives readable failures) over
  custom assertion wrappers, except where `validate_response_code`'s failure-tracking behavior is
  actually wanted.
- Do not introduce unused imports, dead code, or duplicate utilities.
- Preserve documented source-behavior quirks (see e.g. `RecruitResponseHandler.
  post_send_reminder`'s or `ContestResponseHandler`'s module docstring for examples) rather than
  silently "fixing" them — if you believe one is a genuine bug worth fixing, flag it to the user
  first rather than changing behavior unasked.

## Documentation Rules
- Every new module should include a short module-level docstring stating what it does and its
  scope (what domain/endpoints it covers). Don't fabricate a "mirrors <source file>" line unless
  you're actually porting from a known source — for genuinely new endpoints, just describe the
  module's purpose plainly.
- Add function-level docstrings only per the Test Case Design Rules / non-obvious-behavior
  guidance above — for response-handler methods, a one-line docstring naming the HTTP method +
  path is expected (matches existing convention).

## POJO / Typed-Model Rule
This repo has **no pydantic models and no `src/models/` directory** — no endpoint's response is
parsed into a typed model anywhere in the current codebase; responses are read via
`response.json()` / dict access directly in response handlers and tests. Do not introduce
`pydantic` or a `src/models/` package speculatively. If a future task genuinely needs typed
response parsing, raise it with the user first (new dependency + new structural convention) rather
than adding it unasked.

## When Creating New Components
Create a new spec builder / response handler / helper module only if:
- No suitable existing component exists, and
- The existing component cannot be reasonably extended.

In that case: follow existing naming conventions (`<domain>_spec_builder.py`,
`<domain>_response_handler.py`, `src/helpers/<domain>/payloads.py`), keep the implementation
minimal and reusable, and co-locate the file in the correct package under `src/` or `tests/`.

## Final Checklist Before Submission
- Action plan shared and approved before edits.
- Reused existing spec builders/handlers/helpers where possible.
- Correct auth pattern used (API key/secret for `public_apis/*`, `AuthManager` session-cookie for
  `regression/*`) and verified against a sibling endpoint, not guessed.
- New config/test-data values added to `do_api_config.py` / `data.csv`, not hardcoded.
- Added/updated files in the correct folder structure
  (`tests/public_apis/<domain>/`/`tests/regression/<domain>/`, matching `src/` layers).
- New pytest markers registered in `pyproject.toml`.
- New tests sharing mutable server-side state added to the `xdist_group` tagging in
  `tests/regression/conftest.py` if applicable.
- Test code is concise and non-verbose; no TC IDs in test names.
- `log_test_summary(...)` called for new/updated parametrized or field-validating tests.
- No duplicate utility/helper logic introduced.
- No unintended assertion/import/structure rearrangement.
