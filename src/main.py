import datetime
import logging
import time

from . import subscriber
from . import notifs
from . import helper
from .emailer import email_receiver

import requests


def request_api() -> requests.Response:
    """
    :return: The JSON response from the API
    """

    return requests.get("https://fdo.rocketlaunch.live/json/launches/next/5")


def should_exit(config: dict) -> bool:
    """
    :return: If the program should exit
    """

    if not config["exit"]["should_exit"]:
        return False

    exit_datetime = datetime.datetime.combine(datetime.datetime.today(), config["exit"]["exit_time"])

    diff = abs(datetime.datetime.now() - exit_datetime)
    exit_margin = datetime.timedelta(seconds=config["refresh"]["refresh_seconds"] * 3)

    return diff < exit_margin


def main():
    config = helper.config_loader.load_toml("config/config.toml")
    secret = helper.config_loader.load_json("config/secret.json")

    reminder_list = notifs.prelaunch.ReminderList(config, secret)

    # If the API doesn't return 200 here honestly idk what to do
    daily_notifs = notifs.daily.gen_daily_notifs(request_api().json(), config)

    sub = subscriber.subscriber.Subscriber(
        email_receiver.EmailReceiver(secret["sender"]["username"], secret["sender"]["password"]),
        config,
        secret
    )

    while True:
        # Check if the program should exit
        if should_exit(config):
            logging.info("Exiting program")
            break

        # Get the API response for this iteration
        api_response: requests.Response = request_api()

        if api_response.status_code != 200:
            logging.error(f"API error: got status code {api_response.status_code}. Response: {api_response.text}")
            time.sleep(config["refresh"]["refresh_seconds"])
            continue

        # Send daily notifications
        for notif in daily_notifs:
            notif.send(secret)

        # Check for the prelaunch reminders
        reminder_list.update_reminders(api_response.json())

        # Check for subscriptions and unsubscriptions
        secret_changed = sub.check()

        # Update the secret if it changed
        if secret_changed:
            secret = sub.get_secret()
            helper.config_loader.write_json("config/secret.json", sub.get_secret())

        time.sleep(config["refresh"]["refresh_seconds"])


if __name__ == "__main__":
    logging.basicConfig(
        filename="rocket_launch_reminder.log",
        level=logging.INFO,
        format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logging.info("Started")

    try:
        main()

    except Exception as e:
        logging.exception(e)
        raise e
