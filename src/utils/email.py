# src/utils/email.py

import os
import smtplib
from email.message import EmailMessage
import traceback

def send_failure_email(failure_text):
    gmail_user = "tommyethanhowell@gmail.com"
    gmail_app_password = "kfry nwwq csbc qohs"

    msg = EmailMessage()
    msg["Subject"] = "Raycon pipeline FAILED"
    msg["From"] = gmail_user
    msg["To"] = gmail_user
    msg.set_content(failure_text)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(gmail_user, gmail_app_password)
        smtp.send_message(msg)