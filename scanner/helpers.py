from pathlib import Path

import pendulum


def create_directory_with_file(directory_name: str, file_name: str) -> Path:
    directory_path = Path(directory_name)
    directory_path.mkdir(parents=True, exist_ok=True)
    file_path = directory_path / file_name
    return file_path


def convert_iso_to_date_string(iso_string: str) -> str | None:
    """
    Convert an ISO string to a date string.

    Args:
        iso_string (str): The ISO string to convert.

    Returns:
        str: The converted date string.

    Example:
    >>> iso_string = "1987-10-07T00:00:00.000Z"
    >>> date_string = convert_iso_to_date_string(iso_string)
    >>> date_string
    '1987-10-07'

    """
    try:
        dt = pendulum.parse(iso_string)
        return dt.to_date_string()
    except TypeError:
        return None


def get_pay_cycle(schedule_info: dict) -> str | None:
    schedule_key = schedule_info["schedule"]

    pay_cycle_label: str = next(
        (item["label"] for item in schedule_info["schedulesList"] if item["key"] == schedule_key),
        None,
    )
    try:
        return pay_cycle_label.lower()
    except AttributeError:
        return None
