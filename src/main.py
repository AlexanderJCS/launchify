import datetime
import logging
import time

import emailer
import helper

import requests


class Reminder:
    def __init__(self, subject: str, body: str, launch_id: str, time_to_remind: datetime.datetime):
        self.reminder_subject = subject
        self.reminder_body = body
        self.launch_id = launch_id

        self._reminded = False
        self.time_to_remind = time_to_remind

    def should_remind(self) -> bool:
        """
        :return: True if the reminder should go off, False otherwise
        """

        return self._reminded is False and datetime.datetime.now() > self.time_to_remind

    def reminded(self) -> bool:
        """
        :return: Whether the reminder has gone off
        """
        return self._reminded

    def reset_status(self) -> None:
        """
        Sets self._reminded back to False if it is True and self.time_to_remind is after datetime.datetime.now(). This
        is useful if self.time_to_remind was set to a later date.
        """

        if self._reminded is True and datetime.datetime.now() < self.time_to_remind:
            self._reminded = False

    def remind(self, username: str, password: str, to: list[str] | str) -> None:
        """
        Sends an email to the specified recipient(s) with the specified subject and body.

        :param username: The username of the email account to send the email from
        :param password: The password of the email account to send the email from
        :param to: The recipient(s) of the email
        """

        emailer.send_email(username, password, self.reminder_subject, self.reminder_body, to)
        self._reminded = True


class ReminderList:
    def __init__(self, config: dict, secret: dict):
        self._reminders: list[Reminder] = []
        self.config: dict = config
        self.secret: dict = secret

    def get_reminder(self, launch_id: int) -> Reminder | None:
        """
        :param launch_id: The launch ID
        :return: A reminder with the specified launch ID, or None if the reminder is not found
        """
        for reminder in self._reminders:
            if reminder.launch_id == launch_id:
                return reminder

        return None

    def has_launch_id(self, launch_id: int) -> bool:
        """
        :param launch_id: The launch ID
        :return: If the ReminderList has the launch ID
        """

        return self.get_reminder(launch_id) is not None

    def _call_update_method(self) -> None:
        """
        Calls the update method of all reminders in self._reminders.
        """

        for reminder in self._reminders:
            reminder.reset_status()

    def _add_new_reminders(self, api_response: dict):
        for launch_data in api_response["result"]:
            if not self.has_launch_id(launch_data["id"]):
                launch_time = datetime.datetime.fromtimestamp(int(launch_data["sort_date"]))
                remind_time = launch_time - datetime.timedelta(
                    minutes=self.config["general_settings"]["remind_before_launch_mins"]
                )

                self._reminders.append(
                    Reminder(
                        subject=self.config["email"]["before_launch_email"]["subject"],
                        body=format_email(
                            self.config["email"]["before_launch_email"]["email"],
                            launch_data,
                            self.config
                        ),
                        launch_id=launch_data["id"],
                        time_to_remind=remind_time
                    )
                )

    def _update_reminder_time(self, api_response: dict):
        for launch_data in api_response["result"]:
            reminder: Reminder | None = self.get_reminder(launch_data["id"])

            if reminder is None:
                continue

            launch_time = datetime.datetime.fromtimestamp(int(launch_data["sort_date"]))
            remind_time = launch_time - datetime.timedelta(
                minutes=self.config["general_settings"]["remind_before_launch_mins"]
            )

            reminder.time_to_remind = remind_time

    def _remove_completed_reminders(self) -> None:
        """
        Removes reminders once they are 1 hour past their completion time + the remind_before_launch time, and they have
        reminded successfully.
        """

        max_timedelta = datetime.timedelta(
            hours=1,
            minutes=self.config["general_settings"]["remind_before_launch_mins"]
        )

        # Remove all reminders past 1 hour + remind_before_launch_mins
        self._reminders = [
            reminder for reminder in self._reminders
            if not reminder.reminded() or datetime.datetime.now() - reminder.time_to_remind < max_timedelta
        ]

    def update_reminders(self, api_response: dict) -> None:
        """
        Updates all reminders, adds new reminders, and removes all reminders that need to be reminded.
        """

        self._add_new_reminders(api_response)
        self._update_reminder_time(api_response)

        for reminder in self._reminders:
            reminder.reset_status()

            if reminder.should_remind():
                reminder.remind(
                    self.secret["sender"]["username"],
                    self.secret["sender"]["password"],
                    self.secret["receiver"]["emails"]
                )

        self._remove_completed_reminders()


def format_email(template: str, launch_data: dict, config: dict) -> str:
    template = template.format(
        provider=launch_data["provider"]["name"],
        vehicle=launch_data["vehicle"]["name"],
        mission=launch_data["name"],
        launch_pad=launch_data["pad"]["name"],
        launch_site=launch_data["pad"]["location"]["name"],
        remind_before_launch_mins=str(config["general_settings"]["remind_before_launch_mins"])
    )

    launch_datetime = datetime.datetime.fromtimestamp(int(launch_data["sort_date"]))

    template = template.format(
        launch_time=launch_datetime.strftime("%H:%M on %m/%d/%Y")
    )

    return template


def request_api() -> requests.Response:
    """
    :return: The JSON response from the API
    """

    return requests.get("https://fdo.rocketlaunch.live/json/launches/next/5")


def send_daily_notifs(api_data: dict, config: dict, secret: dict) -> None:
    """
    Sends the beginning-of-day report
    :param api_data: The API data
    :param config: The config.toml data
    :param secret: The secret.toml data
    """

    for launch in api_data["result"]:
        now = datetime.datetime.now()
        launch_date = datetime.datetime.fromtimestamp(int(launch["sort_date"]))

        time_til_launch = launch_date - now

        launch_is_too_far = (time_til_launch >
                             datetime.timedelta(hours=config["general_settings"]["launch_report_hours"]))
        launch_already_happened = time_til_launch < datetime.timedelta(seconds=0)

        if launch_is_too_far or launch_already_happened:
            continue

        email = format_email(config["email"]["beginning_of_day_email"]["email"], launch, config)

        emailer.send_email(
            secret["sender"]["username"],
            secret["sender"]["password"],
            config["email"]["beginning_of_day_email"]["subject"],
            email,
            secret["receiver"]["emails"]
        )


def main():
    config = helper.config_loader.load_toml("../config/config.toml")
    secret = helper.config_loader.load_toml("../config/secret.toml")

    reminder_list = ReminderList(config, secret)
    sent_daily_notif = False

    while True:
        # Get the API response for this iteration
        api_response: requests.Response = request_api()

        if api_response.status_code != 200:
            logging.error(f"API error: got status code {api_response.status_code}. Response: {api_response.text}")
            time.sleep(config["general_settings"]["refresh_time_seconds"])
            continue

        # Check if the daily notification should be sent and send it
        # Also reset the sent_daily_notif boolean if
        daily_notif_send_time = config["email"]["beginning_of_day_email"]["send_time"]
        if datetime.datetime.now().time() < daily_notif_send_time:
            sent_daily_notif = False

        elif sent_daily_notif is False:
            logging.info("Sending daily notification")
            send_daily_notifs(api_response.json(), config, secret)

        time.sleep(config["general_settings"]["refresh_time_seconds"])

        # Check for the before-launch reminders
        reminder_list.update_reminders(api_response.json())


if __name__ == "__main__":
    logging.basicConfig(
        filename="rocket_launch_reminder.log",
        level=logging.INFO,
        format="[%(asctime)s] {%(module)s:%(lineno)d} %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    logging.info("Started")
    
    main()
