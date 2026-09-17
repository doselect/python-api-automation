"""
Ports send_email_report.py from https://github.com/doselect/do-api-automation.git as-is (same CLI
shape: `python send_email_report.py <owner> <tag>`, same file paths under `temp/`/`reporting/`),
with only `utils.config` swapped for this repo's `src.core.do_api_config`. Called by `test.sh` at
the end of a Jenkins run — filters `reporting/email_list.csv` for opted-in recipients, filters the
Allure-generated `temp/suites.csv` down to name/status/duration, and emails both plus the
single-file Allure HTML report via Gmail SMTP using REPORT_SENDER_EMAIL/REPORT_SENDER_PASSWORD.
"""
from __future__ import annotations

import datetime
import sys

import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

from src.core.do_api_config import REPORT_SENDER_EMAIL, REPORT_SENDER_PASSWORD, ENVIRONMENT


def filter_csv(input_csv, output_csv, filter_condition, columns_to_keep):
    """Mirrors the source's filter_csv(input_csv, output_csv, filter_condition, columns_to_keep)."""
    df = pd.read_csv(input_csv)
    filtered_df = df.query(filter_condition)[columns_to_keep]
    filtered_df.to_csv(output_csv, index=False)


def fetch_emails_from_csv(csv_file):
    """Mirrors the source's fetch_emails_from_csv(csv_file): opted-in (Status == 'Y') recipients."""
    input_csv = csv_file
    output_csv = "temp/final_mail_list.csv"
    filter_condition = 'Status == "Y"'
    columns_to_keep = ["Email"]
    filter_csv(input_csv, output_csv, filter_condition, columns_to_keep)
    df = pd.read_csv(output_csv)
    return df["Email"].dropna().tolist()


def send_email_with_attachment(sender_email, sender_password, receiver_emails, subject, body, attachments):
    """Mirrors the source's send_email_with_attachment(...): Gmail SMTP, 25MB per-attachment cap."""
    max_attachment_size = 25 * 1024 * 1024  # 25 MB in bytes

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ",".join(receiver_emails)
    msg["Subject"] = subject

    removed_files = []
    for attachment_path in attachments:
        if os.path.getsize(attachment_path) > max_attachment_size:
            removed_files.append(os.path.basename(attachment_path))
            continue

        with open(attachment_path, "rb") as file:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
            msg.attach(part)

    if removed_files:
        body += "\n\nThe following files were removed due to size limit:\n" + "\n".join(removed_files)

    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print(f"Email sent to: {', '.join(receiver_emails)}")


if __name__ == "__main__":
    owner = sys.argv[1]
    tag = sys.argv[2]

    input_csv = "temp/suites.csv"
    output_csv = "temp/test_report.csv"
    filter_condition = 'STATUS != "skipped"'
    columns_to_keep = ["DURATION IN MS", "NAME", "STATUS"]
    filter_csv(input_csv, output_csv, filter_condition, columns_to_keep)

    html_report = "temp/index.html"

    sender_email = REPORT_SENDER_EMAIL  # stored in postactivate file
    sender_password = REPORT_SENDER_PASSWORD  # stored in postactivate file
    email_csv = "reporting/email_list.csv"
    receiver_email = fetch_emails_from_csv(email_csv)

    subject = f"API AUTOMATION {ENVIRONMENT} {tag} report : {datetime.datetime.now()}"
    body = f"Please find the test result for suite execution in the attached CSV. Owner is {owner}"
    attachments = [output_csv, html_report]
    send_email_with_attachment(sender_email, sender_password, receiver_email, subject, body, attachments)
