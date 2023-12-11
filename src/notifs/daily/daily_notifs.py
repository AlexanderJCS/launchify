import datetime
from src import emailer


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
                             datetime.timedelta(hours=config["reminders"]["daily"]["hours_before_launch"]))
        launch_already_happened = time_til_launch < datetime.timedelta(seconds=0)

        if launch_is_too_far or launch_already_happened:
            continue

        body = emailer.format_message(config["reminders"]["daily"]["message"], launch, config)

        emailer.send_email(
            sender=secret["sender"]["username"],
            password=secret["sender"]["password"],
            subject=config["reminders"]["daily"]["subject"],
            body=body,
            to=secret["receiver"]["emails"]
        )
