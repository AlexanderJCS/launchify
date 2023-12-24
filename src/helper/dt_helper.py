import datetime
import zoneinfo


def get_now(config: dict) -> datetime.datetime:
    """
    Returns the current time in the timezone specified in the config file.

    :param config: The config file data
    :return: The current time in the timezone specified in the config file
    """

    return datetime.datetime.now(get_timezone(config))


def get_timezone(config: dict) -> zoneinfo.ZoneInfo:
    """
    Returns the timezone specified in the config file.

    :param config: The config file data
    :return: The timezone specified in the config file
    """

    return zoneinfo.ZoneInfo(config["timezone"])
