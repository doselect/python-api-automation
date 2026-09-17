#!/bin/bash
# Jenkins-driven test runner for python-api-automation, ported from a sibling do-*-automation
# repo's Jenkins runner script (same stash/rerun/report-merge structure), adapted for pytest:
# dropped the `--headless` flag (Selenium-only, meaningless for pure API tests) and simplified the
# ENV -> postactivate-<env>.sh mapping to this repo's actual two files (PRODUCTION vs everything
# else -- postactivate-dev.sh already targets the stg3 environment here, unlike the source repo's
# separate STG2/STG3 files).
# =====================================================
# Configuration
# =====================================================
ALLURE_RESULTS_ROOT="reports"
INITIAL_RESULTS="${ALLURE_RESULTS_ROOT}/initial"
RERUN_RESULTS="${ALLURE_RESULTS_ROOT}/rerun"
ALLURE_REPORT_DIR="allure-report"
TEMP_DIR="temp"
OWNER="Autobot"

if [ $# -lt 2 ]; then
    echo "Usage: $0 <tag> <environment> [rerun]"
    echo "  rerun: true (default) or false. Pass false to skip rerun of failed tests."
    exit 1
fi

TAG=$1
ENV=$2
# Optional 3rd arg: true = run rerun, false = skip rerun (e.g. from Jenkins params.RERUN)
RERUN="${3:-true}"

# =====================================================
# STEP 1: History Preservation & Cleanup
# =====================================================
echo "[INFO] Stashing Allure history"
mkdir -p "$TEMP_DIR/history_stash"
if [ -d "$ALLURE_REPORT_DIR/history" ]; then
    cp -r "$ALLURE_REPORT_DIR/history/." "$TEMP_DIR/history_stash/"
fi

echo "[INFO] Cleaning previous execution artifacts"
rm -rf "$ALLURE_RESULTS_ROOT"
rm -rf "$ALLURE_REPORT_DIR"
rm -rf allure-report-initial allure-report-rerun allure-report-single
rm -rf "$TEMP_DIR"/*.json .pytest_cache
mkdir -p "$TEMP_DIR" "$INITIAL_RESULTS" "$RERUN_RESULTS"

if [ "$(ls -A $TEMP_DIR/history_stash 2>/dev/null)" ]; then
    echo "[INFO] Restoring history to initial results"
    mkdir -p "$INITIAL_RESULTS/history"
    cp -r "$TEMP_DIR/history_stash/." "$INITIAL_RESULTS/history/"
fi

# =====================================================
# STEP 2: Environment Setup
# On CI the pipeline already activates the venv and sources the postactivate for the target env
# before calling this script. Only fall back to local setup if that hasn't happened, so we never
# clobber the pipeline's configuration.
# =====================================================
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -f "venv/bin/activate" ]; then
        echo "[INFO] Activating local venv"
        source venv/bin/activate
    else
        echo "[WARN] No active virtualenv and ./venv not found; using current Python"
    fi
else
    echo "[INFO] Using already-active virtualenv: $VIRTUAL_ENV"
fi

# Source the postactivate for this env only if ENVIRONMENT isn't already set. This repo only has
# two real postactivate files (prod, and dev which targets stg3) -- unlike some sibling repos there
# is no separate stg2/stg3 file to switch on.
if [ -z "$ENVIRONMENT" ]; then
    case "$(echo "$ENV" | tr '[:lower:]' '[:upper:]')" in
        PRODUCTION) POSTACTIVATE="postactivate-prod.sh" ;;
        *)          POSTACTIVATE="postactivate-dev.sh" ;;
    esac
    if [ -f "$POSTACTIVATE" ]; then
        echo "[INFO] Sourcing $POSTACTIVATE for ENV=$ENV"
        source "$POSTACTIVATE"
    else
        echo "[WARN] $POSTACTIVATE not found; assuming environment is already configured"
    fi
else
    echo "[INFO] ENVIRONMENT=$ENVIRONMENT already set; skipping postactivate sourcing"
fi

# =====================================================
# STEP 3: INITIAL RUN & SUMMARY
# =====================================================
echo "================ INITIAL RUN ================"
pytest -n auto -m "$TAG" --alluredir="$INITIAL_RESULTS" || true

# Essential for send_email_report.py (initial_stats)
allure generate "$INITIAL_RESULTS" --clean -o "allure-report-initial"
cp "allure-report-initial/widgets/summary.json" "$TEMP_DIR/initial_summary.json"

# =====================================================
# STEP 4: RERUN & SUMMARY (optional; pass false as 3rd arg to skip)
# =====================================================
is_rerun_enabled() {
    case "$(echo "$RERUN" | tr '[:upper:]' '[:lower:]')" in
        false|0|no) return 1 ;;
        *) return 0 ;;   # true or empty -> enabled
    esac
}

if is_rerun_enabled && [ -f ".pytest_cache/v/cache/lastfailed" ]; then
    echo "================ RERUN FAILED TESTS ================"
    # Inject history into rerun folder to maintain trend continuity
    if [ -d "$INITIAL_RESULTS/history" ]; then
        mkdir -p "$RERUN_RESULTS/history"
        cp -r "$INITIAL_RESULTS/history/." "$RERUN_RESULTS/history/"
    fi

    pytest --last-failed --last-failed-no-failures=none --alluredir="$RERUN_RESULTS" || true

    # Essential for send_email_report.py (rerun_stats)
    allure generate "$RERUN_RESULTS" --clean -o "allure-report-rerun"
    cp "allure-report-rerun/widgets/summary.json" "$TEMP_DIR/rerun_summary.json"
elif ! is_rerun_enabled; then
    echo "[INFO] Rerun skipped (RERUN=$RERUN)"
fi

# =====================================================
# STEP 5: FINAL CONSOLIDATED REPORT & EMAIL ARTIFACTS
# =====================================================
echo "================ GENERATING FINAL REPORTS ================"
# Final report for Jenkins/History persistence
allure generate "$INITIAL_RESULTS" "$RERUN_RESULTS" --clean -o "$ALLURE_REPORT_DIR"

# Final summary and suites.csv for the email script
cp "$ALLURE_REPORT_DIR/widgets/summary.json" "$TEMP_DIR/summary.json"
cp "$ALLURE_REPORT_DIR/data/suites.csv" "$TEMP_DIR/suites.csv"

# Single file report (email attachment)
allure generate --single-file "$INITIAL_RESULTS" "$RERUN_RESULTS" --clean -o allure-report-single
cp allure-report-single/index.html "$TEMP_DIR/index.html"

# =====================================================
# STEP 6: SEND EMAIL & CLEANUP
# =====================================================
python send_email_report.py "$OWNER" "$TAG"

# Cleanup results but keep allure-report for next run's history stash
# Commented out so Jenkins' allure post-step can read raw results after this script exits
# rm -rf "$ALLURE_RESULTS_ROOT"
rm -rf allure-report-initial allure-report-rerun allure-report-single

echo "Test execution completed successfully"
