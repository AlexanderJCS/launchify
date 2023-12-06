import smtplib
import logging

from email.message import EmailMessage


def send_email(sender: str, password: str, subject: str, body: str, to: list[str] | str):
    logging.info("Sending email")

    msg = EmailMessage()

    msg.set_content(body)

    msg["subject"] = subject
    msg["to"] = to
    msg["from"] = sender

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)
