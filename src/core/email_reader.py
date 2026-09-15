"""
Ports utils/email_reader.py from https://github.com/doselect/do-api-automation.git byte-for-byte
(behaviorally): a real IMAP/Gmail-inbox reader used only by the `interview` domain's
email-OTP flow (`src/helpers/interview/email_otp.py`). Genuinely non-REST — no HTTP call, no
RequestSpec/response-handler layering — so it lives in `src/core` as a plain utility, same as
`src/core/do_api_logger.py`.
"""
from __future__ import annotations

import email
import imaplib
import re
from email.header import decode_header
from typing import Any, Dict, List, Optional

import allure
from bs4 import BeautifulSoup

from src.core.do_api_config import AUTOMATION_EMAIL, AUTOMATION_PASSWORD
from src.core.do_api_logger import setup_logger

logger = setup_logger(__name__)


class EmailReader:
    """Mirrors utils.email_reader.EmailReader: a versatile email reader utility that can extract
    various content from emails."""

    def __init__(self, imap_server: str = "imap.gmail.com"):
        self.imap_server = imap_server
        self.mail: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> bool:
        """Connect to email server."""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(AUTOMATION_EMAIL, AUTOMATION_PASSWORD)
            logger.info(f"Connected to {self.imap_server}")
            return True
        except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
            logger.error(f"Failed to connect to email server: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from email server."""
        if self.mail:
            self.mail.close()
            self.mail.logout()

    def get_latest_email_by_subject(self, subject_to_search: str) -> Optional[email.message.Message]:
        """
        Get the latest UNSEEN email with the specified subject.

        `AUTOMATION_EMAIL` is a shared inbox used across the whole interview OTP flow, so searching
        every matching message (regardless of read state) risked picking up a stale email left over
        from an earlier run/attempt — a real message with a real-looking OTP, but one that belonged
        to a different join attempt and the server correctly rejects ("Invalid OTP"). Restricting to
        UNSEEN and letting the RFC822 fetch below mark it \\Seen (its normal side effect, since we
        don't use BODY.PEEK) means each verification email is only ever consumed once.
        """
        try:
            self.mail.select("inbox")
            status, messages = self.mail.search(None, f'(UNSEEN SUBJECT "{subject_to_search}")')

            if status != "OK" or not messages[0]:
                logger.warning(f"No emails found with subject '{subject_to_search}'")
                return None

            # Get the most recent email
            email_ids = messages[0].split()
            latest_email_id = email_ids[-1]

            # Fetch email content
            status, msg_data = self.mail.fetch(latest_email_id, "(RFC822)")
            if status != "OK" or not msg_data[0]:
                logger.error("Failed to fetch email content")
                return None

            return email.message_from_bytes(msg_data[0][1])

        except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
            logger.error(f"Error getting latest email: {e}")
            return None

    def extract_email_content(self, msg: email.message.Message) -> Dict[str, Any]:
        """Extract various content from email message."""
        content: Dict[str, Any] = {
            "subject": "",
            "from": "",
            "to": "",
            "date": "",
            "plain_text": "",
            "html_text": "",
            "links": [],
            "attachments": [],
        }

        try:
            # Extract headers
            content["subject"] = self._decode_header(msg.get("Subject", ""))
            content["from"] = self._decode_header(msg.get("From", ""))
            content["to"] = self._decode_header(msg.get("To", ""))
            content["date"] = msg.get("Date", "")

            # Extract body content
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is not None:
                        # Handle attachments
                        filename = part.get_filename()
                        if filename:
                            content["attachments"].append(filename)
                        continue

                    body = self._get_email_body(part)
                    if body:
                        content_type = part.get_content_type()
                        if content_type == "text/html":
                            content["html_text"] = body
                            # Extract links from HTML
                            content["links"] = self._extract_links_from_html(body)
                        else:
                            content["plain_text"] = body
            else:
                body = self._get_email_body(msg)
                if body:
                    content_type = msg.get_content_type()
                    if content_type == "text/html":
                        content["html_text"] = body
                        content["links"] = self._extract_links_from_html(body)
                    else:
                        content["plain_text"] = body

            # If we have HTML but no plain text, convert HTML to plain text
            if content["html_text"] and not content["plain_text"]:
                content["plain_text"] = self._get_plain_text_from_html(content["html_text"])

        except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
            logger.error(f"Error extracting email content: {e}")

        return content

    def extract_otp(self, text: str) -> Optional[str]:
        """Extract OTP from text using regex patterns."""
        otp_patterns = [
            r"OTP\s*[:\s]*\b(\d{4,6})\b",
            r"Your\s+OTP\s+is\s+\b(\d{4,6})\b",
            r"OTP\s+is\s+\b(\d{4,6})\b",
            r"Code\s*[:\s]*\b(\d{4,6})\b",
            r"Verification\s+code\s*[:\s]*\b(\d{4,6})\b",
            r"\b(\d{4,6})\b.*OTP",
            r"\b(\d{4,6})\b.*verification",
            r"verification\s+code\s*[:\s]*\b(\d{4,6})\b",
            r"access\s+code\s*[:\s]*\b(\d{4,6})\b",
        ]

        for pattern in otp_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def extract_links(self, text: str) -> List[str]:
        """Extract links from text."""
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        return re.findall(url_pattern, text)

    def extract_verification_codes(self, text: str) -> List[str]:
        """Extract verification codes (not just OTP) from text."""
        code_patterns = [
            r"\b(\d{4,8})\b",  # 4-8 digit codes
            r"[A-Z0-9]{6,10}",  # Alphanumeric codes
            r"verification\s+code\s*[:\s]*([A-Z0-9]{4,10})",
            r"access\s+code\s*[:\s]*([A-Z0-9]{4,10})",
        ]

        codes = []
        for pattern in code_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            codes.extend(matches)

        return list(set(codes))  # Remove duplicates

    def _decode_header(self, header: str) -> str:
        """Decode email header."""
        try:
            decoded, encoding = decode_header(header)[0]
            if isinstance(decoded, bytes):
                return decoded.decode(encoding if encoding else "utf-8")
            return str(decoded)
        except Exception:  # noqa: BLE001 - mirrors the source's bare `except:`
            return str(header)

    def _get_email_body(self, part) -> Optional[str]:
        """Get email body content."""
        try:
            body = part.get_payload(decode=True)
            if not body:
                return None

            body = body.decode()
            return body.strip()
        except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
            logger.warning(f"Failed to decode email part: {e}")
            return None

    def _get_plain_text_from_html(self, html_body: str) -> str:
        """Convert HTML email body to plain text."""
        soup = BeautifulSoup(html_body, "html.parser")
        return " ".join(soup.get_text().split())

    def _extract_links_from_html(self, html_body: str) -> List[str]:
        """Extract links from HTML content."""
        soup = BeautifulSoup(html_body, "html.parser")
        links = []
        for link in soup.find_all("a", href=True):
            links.append(link["href"])
        return links


# Convenience functions for backward compatibility (mirrors the module-level functions in
# utils/email_reader.py, same names/signatures).


def get_otp_from_email(subject_to_search: str, imap_server: str = "imap.gmail.com") -> Optional[str]:
    """Extract OTP from email with specified subject (backward compatibility)."""
    reader = EmailReader(imap_server)

    try:
        with allure.step(f"Connecting to {imap_server}"):
            if not reader.connect():
                return None

        with allure.step(f"Searching for emails with subject: {subject_to_search}"):
            msg = reader.get_latest_email_by_subject(subject_to_search)
            if not msg:
                return None

        with allure.step("Extracting OTP from email body"):
            content = reader.extract_email_content(msg)
            otp = reader.extract_otp(content["plain_text"])

            if otp:
                logger.info(f"OTP extracted: {otp}")
                allure.attach(f"OTP found: {otp}", name="OTP Extraction", attachment_type=allure.attachment_type.TEXT)
                return otp
            logger.warning("No OTP found in email body")
            return None

    except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
        error_msg = f"Error in get_otp_from_email: {e}"
        logger.error(error_msg)
        allure.attach(error_msg, name="Email Error", attachment_type=allure.attachment_type.TEXT)
        return None
    finally:
        reader.disconnect()


def get_email_content(subject_to_search: str, imap_server: str = "imap.gmail.com") -> Optional[Dict[str, Any]]:
    """Get complete email content for specified subject."""
    reader = EmailReader(imap_server)

    try:
        if not reader.connect():
            return None

        msg = reader.get_latest_email_by_subject(subject_to_search)
        if not msg:
            return None

        content = reader.extract_email_content(msg)

        # Extract additional information
        content["otp"] = reader.extract_otp(content["plain_text"])
        content["verification_codes"] = reader.extract_verification_codes(content["plain_text"])

        return content

    except Exception as e:  # noqa: BLE001 - mirrors the source's catch-all
        logger.error(f"Error in get_email_content: {e}")
        return None
    finally:
        reader.disconnect()


def extract_verification_codes_from_email(subject_to_search: str, imap_server: str = "imap.gmail.com") -> List[str]:
    """Extract all verification codes from email with specified subject."""
    content = get_email_content(subject_to_search, imap_server)
    if content:
        return content.get("verification_codes", [])
    return []


def extract_links_from_email(subject_to_search: str, imap_server: str = "imap.gmail.com") -> List[str]:
    """Extract all links from email with specified subject."""
    content = get_email_content(subject_to_search, imap_server)
    if content:
        return content.get("links", [])
    return []
