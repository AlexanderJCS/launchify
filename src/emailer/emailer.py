import datetime
import smtplib
import logging

from email.message import EmailMessage


def send_email(sender: str, password: str, subject: str, body: str, to: list[str] | str):
    logging.info("Sending reminder")

    msg = EmailMessage()

    msg.set_content(body)

    msg["subject"] = subject
    msg["to"] = to
    msg["from"] = sender

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)


def format_message(template: str, launch_data: dict, config: dict) -> str:
    launch_datetime = datetime.datetime.fromtimestamp(int(launch_data["sort_date"]))

    template = template.format(
        provider=launch_data["provider"]["name"],
        vehicle=launch_data["vehicle"]["name"],
        mission=launch_data["name"],
        launch_pad=launch_data["pad"]["name"],
        launch_site=launch_data["pad"]["location"]["name"],
        remind_before_launch_mins=str(config["general_settings"]["remind_before_launch_mins"]),
        launch_time=launch_datetime.strftime("%H:%M on %m/%d/%Y")
    )

    return template
