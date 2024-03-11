import datetime
import zoneinfo


def load_isoformat(isoformat: str, to_convert: zoneinfo.ZoneInfo) -> datetime.datetime:
    """
    Loads a datetime.datetime object from an ISO 8601 formatted string. Assumes the time is in UTC and will convert it
    to the timezone specified in the argument.

    :param isoformat: The ISO 8601 formatted string
    :param to_convert: The timezone to convert the time to
    :return: The datetime.datetime object
    """

    return datetime.datetime.fromisoformat(isoformat).replace(tzinfo=zoneinfo.ZoneInfo("UTC")).astimezone(to_convert)


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
