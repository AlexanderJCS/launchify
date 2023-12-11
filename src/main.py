import datetime
import logging
import time

from . import notifs
from . import helper

import requests


def request_api() -> requests.Response:
    """
    :return: The JSON response from the API
    """

    return requests.get("https://fdo.rocketlaunch.live/json/launches/next/5")


def main():
    config = helper.config_loader.load_toml("config/config.toml")
    secret = helper.config_loader.load_toml("config/secret.toml")

    reminder_list = notifs.prelaunch.ReminderList(config, secret)
    sent_daily_notif = False

    while True:
        # Check if the program should exit

        should_exit = config["exit"]["should_exit"]
        exit_datetime = datetime.datetime.combine(datetime.datetime.today(), config["exit"]["exit_time"])
        if should_exit and abs(datetime.datetime.now() - exit_datetime) < datetime.timedelta(minutes=5):
            logging.info("Exiting main loop")
            break

        # Get the API response for this iteration
        api_response: requests.Response = request_api()

        if api_response.status_code != 200:
            logging.error(f"API error: got status code {api_response.status_code}. Response: {api_response.text}")
            time.sleep(config["refresh"]["refresh_seconds"])
            continue

        # Check if the daily notification should be sent and send it
        # Also reset the sent_daily_notif boolean if
        daily_notif_send_time = config["reminders"]["daily"]["send_time"]
        if datetime.datetime.now().time() < daily_notif_send_time:
            sent_daily_notif = False

        elif sent_daily_notif is False:
            logging.info("Sending daily notification")
            notifs.daily.send_daily_notifs(api_response.json(), config, secret)
            sent_daily_notif = True

        # Check for the before-launch reminders
        reminder_list.update_reminders(api_response.json())

        time.sleep(config["refresh"]["refresh_seconds"])


if __name__ == "__main__":
    logging.basicConfig(
        filename="rocket_launch_reminder.log",
        level=logging.INFO,
        format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logging.info("Started")
    
    main()
