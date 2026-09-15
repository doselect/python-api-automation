"""
The `sec-ch-ua*`/`sec-fetch-*`/`user-agent` block that utils/header_generator.py
(https://github.com/doselect/do-api-automation.git) repeats verbatim across dozens of its
per-endpoint `get_*_headers(shared_data)` functions for the session-cookie-auth domains
(recruit/interview/hacker/contest/doiq/ai_interview/content_creator). Factored into one constant
here instead of re-pasting the identical dict in every ported spec builder — same values, not a
refactor of behavior.
"""
from __future__ import annotations

CHROME_WINDOWS_FINGERPRINT_HEADERS: dict[str, str] = {
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
    ),
}

# A second, distinct fingerprint block header_generator.py/the ai_interview regression_api_methods
# use for several endpoints (get_latest_ai_interview, post_bulk_invite*, post_invite_ai_interview,
# post_single_invite_no_cv) — Linux/Chrome-129 rather than Windows/Chrome-134. Kept separate since
# it's a different literal value, not a formatting variant of the one above.
CHROME_LINUX_FINGERPRINT_HEADERS: dict[str, str] = {
    "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Linux"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    ),
}
