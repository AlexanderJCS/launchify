import datetime

from src.helper import dt_helper
from src import emailer
from src import notifs


class DailyNotif:
    def __init__(self, config: dict, launch_data: dict):
        """
        Initializes the DailyNotif object.

        :param config: The configuration file data
        :param launch_data: The launch data from the API. launch_data["t0"] must not be a string.
        """

        self.reminder: notifs.Reminder = notifs.Reminder(
            subject=config["reminders"]["daily"]["subject"],
            body=emailer.format_message(config["reminders"]["daily"]["message"], launch_data, config),
            launch_id=launch_data["id"],
            time_to_remind=datetime.datetime.combine(
                datetime.date.today(),
                config["reminders"]["daily"]["send_time"],
                tzinfo=dt_helper.get_timezone(config)
            ),
            config=config
        )

    def send(self, secret: dict) -> None:
        """
        Sends daily notifications if they should send.
        """

        if self.reminder.should_remind():
            self.reminder.remind(
                secret["sender"]["username"],
                secret["sender"]["password"],
                secret["receiver"]["emails"]
            )


def gen_daily_notifs(api_data: dict, config: dict) -> list[DailyNotif]:
    """
    Sends the beginning-of-day report
    :param api_data: The API data
    :param config: The config.toml data
    """

    daily_notifs: list[DailyNotif] = []

    for launch in api_data["result"]:
        now = dt_helper.get_now(config)

        if not isinstance(launch["t0"], str):
            continue

        launch_date = datetime.datetime.fromisoformat(launch["t0"])

        time_to_launch = launch_date - now

        launch_is_too_far = time_to_launch > datetime.timedelta(
            hours=config["reminders"]["daily"]["hours_before_launch"]
        )

        launch_already_happened = time_to_launch < datetime.timedelta(seconds=0)

        if launch_is_too_far or launch_already_happened:
            continue

        daily_notifs.append(
            DailyNotif(config, launch)
        )

    return daily_notifs
