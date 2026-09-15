"""
Ports utils/auth.py from https://github.com/doselect/do-api-automation.git: the session-cookie +
CSRF login used by every `regression`-marked (non-public-API) domain — recruit, interview,
hacker, contest, doiq, ai_interview, content_creator all authenticate this way (as opposed to the
DoSelect-Api-Key/Secret header auth used by the `public_apis/*` domains).

Scrapes the login page for a Django CSRF token, POSTs credentials, and pulls the resulting
`sessionid` cookie — same flow as the source, byte-for-byte.
"""
from __future__ import annotations

from typing import Dict

import requests
from bs4 import BeautifulSoup

from src.core.do_api_config import ACCOUNT_TYPE, AUTH_URL, DOSELECT_PRIMARY_DOMAIN, ENVIRONMENT, PRODUCT_TYPE
from src.core.do_api_logger import setup_logger


class AuthManager:
    """Mirrors utils.auth.AuthManager."""

    def __init__(
        self,
        account_email: str,
        account_password: str,
        base_url: str = DOSELECT_PRIMARY_DOMAIN,
        auth_url: str = AUTH_URL,
        environment: str = ENVIRONMENT,
        account_type: str = ACCOUNT_TYPE,
        product_type: str = PRODUCT_TYPE,
    ):
        self.base_url = base_url
        self.auth_url = auth_url
        self.environment = environment
        self.account_type = account_type
        self.product_type = product_type
        self.account_email = account_email
        self.account_password = account_password
        self._csrf_token = None
        self._session_id = None
        self._headers = None
        self._cookie = None
        self.logger = setup_logger(__name__)
        self.session = requests.Session()

    def authenticate(self) -> None:
        """Authenticate and store session details"""
        login_url = f"{self.base_url}/login"
        try:
            response = self.session.get(login_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Failed to load login page: {e}")

        soup = BeautifulSoup(response.content, "html.parser")
        input_tag = soup.find(attrs={"name": "csrfmiddlewaretoken"})
        if not input_tag:
            raise Exception("CSRF token not found in login page")

        self._csrf_token = input_tag["value"]

        payload = {
            "csrfmiddlewaretoken": self._csrf_token,
            "login": self.account_email,
            "password": self.account_password,
        }

        headers = {
            "content-type": "application/x-www-form-urlencoded",
            "referer": login_url,
        }

        self.session.cookies.set("doselectcsrf", self._csrf_token)

        try:
            post_response = self.session.post(
                login_url,
                headers=headers,
                data=payload,
                allow_redirects=False,
                timeout=10,
            )
        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}")
        if post_response.status_code != 302:
            raise Exception(f"Login failed with status code: {post_response.status_code}")

        self._session_id = post_response.cookies.get("sessionid")
        if not self._session_id:
            self.logger.info(f"Session ID not found in cookies after login : {post_response}")
            raise Exception("Session ID not found after login")

        self._cookie = f"sessionid={self._session_id}; doselectcsrf={self._csrf_token}"

        self._headers = {
            "accept": "application/json",
            "content-type": "application/json;charset=UTF-8",
            "cookie": self._cookie,
            "origin": self.base_url,
            "referer": self.base_url,
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/110.0.0.0 Safari/537.36"
            ),
        }

    def refresh_authentication(self) -> None:
        """Forces a fresh login to get new session and CSRF token"""
        self._csrf_token = None
        self._session_id = None
        self._headers = None
        self._cookie = None
        self.session.cookies.clear()
        self.authenticate()

    @property
    def headers(self) -> Dict[str, str]:
        if not self._headers:
            self.authenticate()
        return self._headers

    @property
    def cookie(self) -> str:
        if not self._cookie:
            self.authenticate()
        return self._cookie

    @property
    def csrf_token(self) -> str:
        if not self._csrf_token:
            self.authenticate()
        return self._csrf_token

    @property
    def session_id(self) -> str:
        if not self._session_id:
            self.authenticate()
        return self._session_id
