"""
NexoraFuture Email Sender
Sends daily digest via Gmail SMTP.
Copyright 2026 NexoraFuture. All rights reserved.
"""

import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from platforms.email_digest import generate_html_digest, generate_plaintext_digest

# Email config via environment variables
SMTP_EMAIL = os.environ.get("NF_SMTP_EMAIL", "")  # e.g. ukclarityfinance@gmail.com
SMTP_PASSWORD = os.environ.get("NF_SMTP_PASSWORD", "")  # Gmail App Password
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
DIGEST_RECIPIENTS = os.environ.get(
    "NF_DIGEST_RECIPIENTS", "malik_priyanka91@yahoo.in"
)


def send_digest(recipients=None):
    """Send the daily digest email."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        print("ERROR: Email credentials not configured.")
        print("Set these environment variables:")
        print("  NF_SMTP_EMAIL=your_gmail@gmail.com")
        print("  NF_SMTP_PASSWORD=your_gmail_app_password")
        print()
        print("To get an App Password:")
        print("  1. Go to https://myaccount.google.com/apppasswords")
        print("  2. Create one for 'NexoraFuture Automation'")
        print("  3. Copy the 16-character password")
        return False

    if recipients is None:
        recipients = [r.strip() for r in DIGEST_RECIPIENTS.split(",")]

    today = date.today()
    days_left = config.days_until_deadline()
    subject = f"NexoraFuture Daily Digest — {today.strftime('%B %d')} | {days_left} Days to MTD Deadline"

    # Build email
    msg = MIMEMultipart("alternative")
    msg["From"] = f"NexoraFuture <{SMTP_EMAIL}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # Attach plain text and HTML versions
    plaintext = generate_plaintext_digest()
    html = generate_html_digest()

    msg.attach(MIMEText(plaintext, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Send
    try:
        print(f"Connecting to {SMTP_SERVER}...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)

        server.sendmail(SMTP_EMAIL, recipients, msg.as_string())
        server.quit()

        print(f"Digest sent successfully!")
        print(f"  From: {SMTP_EMAIL}")
        print(f"  To: {', '.join(recipients)}")
        print(f"  Subject: {subject}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("ERROR: Authentication failed.")
        print("Make sure you're using a Gmail App Password, not your regular password.")
        print("Get one at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="NexoraFuture Email Sender")
    parser.add_argument("--send", action="store_true", help="Send daily digest")
    parser.add_argument("--to", type=str, help="Override recipient email")
    args = parser.parse_args()

    recipients = [args.to] if args.to else None
    send_digest(recipients=recipients)
