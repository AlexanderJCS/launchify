import smtplib
import logging

from src.helper import dt_helper
from email.message import EmailMessage


def send_email(sender: str, password: str, subject: str, body: str, to: list[str] | str):
    if isinstance(to, str):
        logging.info(f"Sending email to {to}: subject: {subject}")
    elif isinstance(to, list):
        logging.info(f"Sending email to {len(to)} recipients: subject: {subject}")

    msg = EmailMessage()

    msg.set_content(body)

    msg["subject"] = subject
    msg["bcc"] = to
    msg["from"] = sender

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login(sender, password)
        smtp.send_message(msg)


def format_message(template: str, launch_data: dict, config: dict) -> str:
    """
    Formats the message to be sent to the user.

    :param template: The template to format
    :param launch_data: The launch data from the API. launch_data["t0"] must not be None.
    :param config: The config toml file.
    :return: The formatted message.
    """

    launch_datetime = dt_helper.load_isoformat(launch_data["t0"], dt_helper.get_timezone(config))

    template = template.format(
        provider=launch_data["provider"]["name"],
        vehicle=launch_data["vehicle"]["name"],
        mission=launch_data["name"],
        launch_pad=launch_data["pad"]["name"],
        launch_site=launch_data["pad"]["location"]["name"],
        remind_before_launch_mins=str(config["reminders"]["prelaunch"]["mins_before_launch"]),
        launch_time=launch_datetime.strftime("%H:%M on %m/%d/%Y")
    )

    return template
