import datetime
import logging

from src.helper import dt_helper
from src import emailer


class Reminder:
    def __init__(self, subject: str, body: str, launch_id: str, time_to_remind: datetime.datetime, config: dict):
        """
        Initializes the Reminder object.

        :param subject: The subject of the reminder message
        :param body: The body of the reminder message
        :param launch_id: The unique launch ID
        :param time_to_remind: A timezone-aware datetime.datetime object
               (several methods will not work with timezone-naive datetime.datetime objects)
        :param config: The config file data
        """

        self.reminder_subject = subject
        self.reminder_body = body
        self.launch_id = launch_id
        self.config = config

        self._reminded = False
        self.time_to_remind = time_to_remind

    def should_remind(self) -> bool:
        """
        The conditions for if the notification should go off are:
        1. The notification has not gone off yet
        2. The current time is past the time to remind
        3. The current time is not more than 2 * refresh_seconds past the time to remind

        :return: True if the notifs should go off, False otherwise
        """

        return self._reminded is False \
            and dt_helper.get_now(self.config) > self.time_to_remind \
            and dt_helper.get_now(self.config) - self.time_to_remind < datetime.timedelta(
                seconds=self.config["refresh"]["refresh_seconds"] * 2
            )

    def reminded(self) -> bool:
        """
        :return: Whether the notifs has gone off
        """
        return self._reminded

    def reset_status(self) -> None:
        """
        Sets self._reminded back to False if it is True and self.time_to_remind is at least 1 hour in the future. This
        is useful if self.time_to_remind was set to a later date.
        """

        if (self._reminded is True and
                self.time_to_remind - dt_helper.get_now(self.config) > datetime.timedelta(hours=1)):

            logging.info(f"Resetting reminder status for ID {self.launch_id}, time to remind: {self.time_to_remind}")
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
