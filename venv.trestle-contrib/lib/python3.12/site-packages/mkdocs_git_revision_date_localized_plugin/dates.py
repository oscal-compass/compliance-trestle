from datetime import datetime, timezone
from typing import Any

from babel.dates import format_date, format_datetime, get_timezone


def get_date_formats(
    unix_timestamp: float, locale: str = "en", time_zone: str = "UTC", custom_format: str = "%d. %B %Y"
) -> dict[str, Any]:
    """
    Calculate different date formats / types.

    Args:
        unix_timestamp (float): A timestamp in seconds since 1970. Assumes UTC.
        locale (str): Locale code of language to use. Defaults to 'en'.
        time_zone (str): Timezone database name (https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
        custom_format (str): strftime format specifier for the 'custom' type

    Returns:
        dict: Different date formats.
    """
    assert time_zone is not None
    assert locale is not None

    # Normalize locale for Babel: convert hyphens to underscores (e.g., pt-BR -> pt_BR)
    # This is needed for compatibility with mkdocs-static-i18n and other plugins
    # that may use hyphenated locale codes, while Babel expects underscores
    if locale:
        locale = str(locale).replace("-", "_")

    utc_revision_date = datetime.fromtimestamp(int(unix_timestamp), tz=timezone.utc)
    loc_revision_date = utc_revision_date.replace(tzinfo=get_timezone("UTC")).astimezone(get_timezone(time_zone))

    return {
        "date": format_date(loc_revision_date, format="long", locale=locale),
        "datetime": " ".join(
            [
                format_date(loc_revision_date, format="long", locale=locale),
                loc_revision_date.strftime("%H:%M:%S"),
            ]
        ),
        "datetime-timezone": " ".join(
            [
                format_date(loc_revision_date, format="long", locale=locale),
                loc_revision_date.strftime("%H:%M:%S %Z"),
            ]
        ),
        "iso_date": loc_revision_date.strftime("%Y-%m-%d"),
        "iso_datetime": loc_revision_date.strftime("%Y-%m-%d %H:%M:%S"),
        "timeago": f'<span class="timeago" datetime="{loc_revision_date.isoformat()}" locale="{locale}"></span>',
        "custom": format_datetime(loc_revision_date, format=strftime_to_babel_format(custom_format), locale=locale),
    }


def strftime_to_babel_format(fmt: str) -> str:
    """
    Convert strftime format string to Babel format pattern.

    Args:
        fmt (str): strftime format string

    Returns:
        str: Babel format pattern
    """
    # Dictionary mapping strftime directives to Babel format patterns
    mapping = {
        "%a": "EEE",  # Weekday abbreviated
        "%A": "EEEE",  # Weekday full
        "%b": "MMM",  # Month abbreviated
        "%B": "MMMM",  # Month full
        "%c": "",  # Locale's date and time (not directly mappable)
        "%d": "dd",  # Day of month zero-padded
        "%-d": "d",  # Day of month
        "%e": "d",  # Day of month space-padded
        "%f": "SSSSSS",  # Microsecond
        "%H": "HH",  # Hour 24h zero-padded
        "%-H": "H",  # Hour 24h
        "%I": "hh",  # Hour 12h zero-padded
        "%-I": "h",  # Hour 12h
        "%j": "DDD",  # Day of year
        "%m": "MM",  # Month zero-padded
        "%-m": "M",  # Month
        "%M": "mm",  # Minute zero-padded
        "%-M": "m",  # Minute
        "%p": "a",  # AM/PM
        "%S": "ss",  # Second zero-padded
        "%-S": "s",  # Second
        "%w": "e",  # Weekday as number
        "%W": "w",  # Week of year
        "%x": "",  # Locale's date (not directly mappable)
        "%X": "",  # Locale's time (not directly mappable)
        "%y": "yy",  # Year without century
        "%Y": "yyyy",  # Year with century
        "%z": "Z",  # UTC offset
        "%Z": "z",  # Timezone name
        "%%": "%",  # Literal %
    }

    result = fmt
    for strftime_code, babel_code in mapping.items():
        result = result.replace(strftime_code, babel_code)

    return result
