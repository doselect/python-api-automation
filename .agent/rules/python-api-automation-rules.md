# Python API Automation Rules

## Purpose
Use these rules whenever creating or updating API automation in `python-api-automation/`, the
pytest/RestAssured-style port of the Java `serenity-rest-assured` framework's structure and
conventions. Adapted from `.agent/rules/serenity-api-automation-rules.md` in the Java project —
same core principles, translated to Python/pytest/pydantic/Allure idioms.

## Core Principles
- Follow the conventions established in this project (mirrors of the Java framework's spec
  builder / response handler / test layering).
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
- Never modify anything under the Java `src/`, `pom.xml`, or any other pre-existing file in the
  repository root from this project — `python-api-automation/` is additive only.

## Fact-Only Guardrails (Mandatory)
- Do not fabricate or assume assertions, API endpoints, URLs, credentials, tokens, headers,
  payload fields, expected status codes, or test data.
- Use only facts explicitly provided by the user or already present in the codebase/config files
  (including the Java framework this project mirrors).
- If any required detail is missing, pause and ask the user for the exact value, or leave a
  clearly marked `# TODO` comment — never guess a plausible-looking value.
- Do not infer secrets or environment-specific values.
- Do not create placeholder credentials in code.
- Keep implementation strictly aligned with user-provided requirements and existing framework
  facts (Java source, `config.properties`, resource files).

## Framework Structure (Short Reference)
- `src/specs/*_spec_builder.py`: creates reusable `RequestSpec` objects (base URL, base path,
  default headers, timeout config) — mirrors `specs/*SpecBuilder` (Java).
- `src/responses/*_response_handler.py`: executes API calls (via `core/rest_client.py`) and
  centralizes path/query param mapping — mirrors `responses/*ResponseHandler` (Java).
- `tests/.../test_*.py`: assertion layer only (status/schema/business checks, negative scenarios,
  response time, etc.) — mirrors `tests/.../*APITest` (Java).
- `src/helpers/...`: reusable business logic, validators, verifiers — mirrors `helpers/...` (Java).
- `src/constants/paths/*_api_path.py`: endpoint paths, base-URL resolvers — mirrors
  `constants/paths/*APIPath` (Java).
- `src/constants/headers/*`: shared header keys/values — mirrors `constants/headers/*` (Java).
- `tests/data/...`: CSV/JSON test data — mirrors `src/test/resources/data/...` (Java).
- `tests/schema/...`: response schema files — mirrors `src/test/resources/schema/...` (Java).
- `src/models/<domain>/`: pydantic response models used for typed validation — mirrors
  `src/test/java/pojos/<domain>/` (Java, response-POJOs-for-assertions case).
- `src/core/`: shared infrastructure — `base_spec_builder.py` (mirrors `BaseSpecBuilder`),
  `rest_client.py` (mirrors `RestClient`), `file_io_utils.py` (mirrors `FileIOUtils`).
- `src/reports/report_utils.py`: builds the Allure summary table — mirrors `ReportUtils` /
  `Serenity.recordReportData()` (Java).

## Mandatory Flow For New API Tests
1. **Check existing implementation first**: search for an existing spec builder, response
   handler, helper, verifier, model, schema, or constants module. Reuse before creating anything
   new.
2. **Spec builder pattern for request setup**: do not build request specs directly inside test
   functions. Add/extend endpoint configuration in the relevant `src/specs/*_spec_builder.py`
   class, built on `src/core/base_spec_builder.py`'s `build_request_spec` / `get_default_headers`.
3. **Response handler pattern for API invocation**: keep raw API calls in
   `src/responses/*_response_handler.py` classes. Keep test functions focused on assertions and
   scenario validation only.
4. **Keep test logic clean**: arrange test data, execute through the handler, assert the outcome.
   Prefer `pytest.mark.parametrize` and data-driven coverage where applicable. Validate status
   code, response body/schema, and critical business checks.

## Folder Structure Rules
- `src/core/` — shared infra (spec builder base, REST client, config-file reader).
- `src/constants/paths/` — endpoint path constants + base-URL resolvers.
- `src/constants/headers/` — shared header keys/values.
- `src/specs/` — per-domain spec builders.
- `src/responses/` — per-domain response handlers.
- `src/helpers/<domain>/verifier/` — reusable business-logic verifiers.
- `src/models/<domain>/` — pydantic response models (see Model Location Rule below).
- `src/reports/` — reporting helpers (Allure table builder).
- `tests/<domain>/<page>/test_*.py` — feature-based test files.
- `tests/data/...` — CSV/JSON test data (mirrors `src/test/resources/data/...`).
- `tests/schema/...` — JSON schema files (mirrors `src/test/resources/schema/...`).
- Always place new files in the correct existing package structure; do not introduce a
  parallel/duplicate structure for the same purpose.

## Model (Pydantic) Location Rule (Mandatory)
- Response models consumed only by test/verifier code (typed extraction of API responses for
  assertions) live under `src/models/<domain>/` — the Python equivalent of
  `src/test/java/pojos/<domain>/`.
- Use pydantic v2 `BaseModel` with `model_config = ConfigDict(populate_by_name=True, extra=
  "ignore")` (mirrors Jackson's `@JsonIgnoreProperties(ignoreUnknown = true)`), and
  `Field(alias=..., validation_alias=AliasChoices(...))` where the Java POJO uses `@JsonAlias`.
- Request-body models shared across response handlers and tests would live under
  `src/models/<domain>/` as well in this Python port (there is no main/test source-set split as
  in the Java Maven project) — document in the module docstring whether a model is
  request- or response-facing.

## Reporting Format Rule (Mandatory)
Adapted from the Java framework's "Serenity Report Output Format": every test that accepts input
parameters or validates a response must attach a structured tabular summary to the Allure report
via `src.reports.report_utils.log_test_summary(title, rows)`.

- `rows` is a list of dicts, each with keys: `input`, `expected_status`, `actual_status`,
  `field_check`, `result` — mirrors the Java table's columns (`Input | Expected Status | Actual
  Status | Field Check | Result`).
- Call `log_test_summary(...)` at the end of each test function (one call per test, one row per
  scenario/iteration for parametrized tests).
- Title must identify the scenario, e.g. `"Salary Data API - Happy Path"`.
- If a test only validates schema/status (no business fields), still record input params +
  status + a `field_check` describing what was checked (e.g. `"schema valid"`, `"N/A"`).
- Prefer the shared `log_test_summary` helper over duplicating table-building logic across test
  modules.

## Test Case Design Rules (Mandatory)
- No TC IDs in test function names (no `_TC001`-style suffixes).
- Test files are **feature-based**, not endpoint-based: one file covers all scenarios for a
  feature/page (mirrors the Java rule against per-endpoint test files).
- Every test function must have a docstring explaining what it validates and why — not restating
  trivial code, but the business/API intent (mirrors the Java Javadoc-per-test rule).
- Each test function must assert something unique that no other test in the file covers; club
  scenarios to eliminate redundancy (e.g. don't add a standalone 200-status test if 200 is already
  implicitly required for the test to proceed).
- Use `pytest.mark.skip(reason=...)` / `pytest.mark.xfail(reason=...)` with a clear explanatory
  message for tests that need external setup — never leave a skip/xfail with an empty or vague
  reason (mirrors the Java `@Disabled` rule).
- Prefer `pytest.mark.parametrize` reading from a CSV/data file (via a small loader function) as
  the Python equivalent of JUnit's `@CsvFileSource(numLinesToSkip = 1)`.

## Reusability Rules
- Before adding a new utility/helper module, search existing `src/helpers`, `src/core`,
  `src/specs`, and `src/constants` packages.
- If similar logic exists, extend/refactor that module instead of duplicating.
- New shared logic must go into a reusable module under `src/`, not copied across test files.

## Code Quality Rules
- Avoid hardcoded values when constants/config already exist (`src/constants/...`,
  `config.properties` via `file_io_utils.get_property_value`).
- Keep functions small and purpose-driven.
- Use meaningful names for test functions, data files, and helper functions.
- Prefer plain `assert` statements (pytest's assertion rewriting gives readable failures) over
  custom assertion wrappers, matching the framework-consistent style.
- Do not introduce unused imports, dead code, or duplicate utilities.

## Documentation Rules
- Every new module should include a short module-level docstring stating its Java-framework
  equivalent (what it mirrors) and any scope limitations.
- Add function-level docstrings for anything with non-obvious behavior or business validation.
- Documentation must explain intent and business validation, not restate trivial code.

## When Creating New Components
Create a new spec builder / response handler / helper / model only if:
- No suitable existing component exists, and
- The existing component cannot be reasonably extended.

In that case: follow existing naming conventions, keep the implementation minimal and reusable,
and co-locate the file in the correct package under `src/` or `tests/`.

## Final Checklist Before Submission
- Action plan shared and approved before edits.
- Reused existing spec builders/handlers/helpers/models where possible.
- Added/updated files in the correct folder structure.
- Test code is concise and non-verbose.
- Added useful documentation (module-level + function-level docstrings).
- No TC IDs in test function names.
- No duplicate utility/helper logic introduced.
- Every parametrized/response-validating test calls `log_test_summary(...)`.
- No unintended assertion/import/structure rearrangement.
