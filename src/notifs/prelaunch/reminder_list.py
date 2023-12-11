import datetime
from .reminder import Reminder
from src import emailer


class ReminderList:
    def __init__(self, config: dict, secret: dict):
        self._reminders: list[Reminder] = []
        self.config: dict = config
        self.secret: dict = secret

    def get_reminder(self, launch_id: int) -> Reminder | None:
        """
        :param launch_id: The launch ID
        :return: A notifs with the specified launch ID, or None if the notifs is not found
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
                        subject=self.config["reminders"]["prelaunch"]["subject"],
                        body=emailer.format_message(
                            self.config["reminders"]["prelaunch"]["message"],
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
        Removes reminders once they are 1 hour past their completion time + the remind_before_launch time, effectively
        removing the reminder 1 hour after launch
        """

        max_timedelta = datetime.timedelta(
            hours=1,
            minutes=self.config["general_settings"]["remind_before_launch_mins"]
        )

        # Remove all reminders past 1 hour + remind_before_launch_mins
        self._reminders = [
            reminder for reminder in self._reminders
            if datetime.datetime.now() - reminder.time_to_remind < max_timedelta
        ]

    def update_reminders(self, api_response: dict) -> None:
        """
        Updates all reminders, adds new reminders, and removes all reminders that need to be reminded.
        """

        self._add_new_reminders(api_response)
        self._update_reminder_time(api_response)

        # Update all reminders
        for reminder in self._reminders:
            reminder.reset_status()

        self._remove_completed_reminders()

        # Notify all reminders that should be reminded
        for reminder in self._reminders:
            if reminder.should_remind():
                reminder.remind(
                    self.secret["sender"]["username"],
                    self.secret["sender"]["password"],
                    self.secret["receiver"]["emails"]
                )
