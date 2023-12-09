import datetime

from .. import emailer


class Reminder:
    def __init__(self, subject: str, body: str, launch_id: str, time_to_remind: datetime.datetime):
        self.reminder_subject = subject
        self.reminder_body = body
        self.launch_id = launch_id

        self._reminded = False
        self.time_to_remind = time_to_remind

    def should_remind(self) -> bool:
        """
        :return: True if the notifs should go off, False otherwise
        """

        return self._reminded is False and datetime.datetime.now() > self.time_to_remind

    def reminded(self) -> bool:
        """
        :return: Whether the notifs has gone off
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
