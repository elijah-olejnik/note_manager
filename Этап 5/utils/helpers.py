import uuid
from datetime import datetime
from .enums import NoteStatus
from resources import strings


def str_to_date(str_date, is_deadline=True):
    """The function converts user input string to a datetime
    object. If is_deadline=True the function compare the entered data
    with datetime.now() to assure that deadline is in the future.
    Raises ValueError if input doesn't fit date format or the deadline condition.
    """
    try:
        date = datetime.strptime(str_date, "%d-%m-%Y %H:%M")
        if is_deadline and date <= (datetime.now()):
            raise ValueError(strings.deadline_invalid_str)
        return date
    except ValueError as e:
        raise e


def date_to_str(date, is_deadline, state=NoteStatus.TERMLESS):
    """The function convert the datetime object to string or return
    NO DEADLINE if note status is TERMLESS or COMPLETED. If deadline
    parameter is False, the function just convert datetime to string.
    """
    if not is_deadline or state not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
        return datetime.strftime(date, "%B %d, %Y %H:%M")
    else:
        return strings.no_deadline_str


def input_to_enum_value(input_str, enum_class):
    """The function convert the user input to an enum value or value name
    of a given Enum in the second argument. Raises the ValueError if
    the given data doesn't match with any of Enum values or names.
    """
    try:
        if not input_str.isdigit():
            name = input_str.upper()
            return enum_class[name]
        else:
            value = int(input_str)
            return enum_class(value)
    except (KeyError, ValueError) as e:
        raise ValueError(strings.enum_error_str + str(e))


def generate_id():
    """The function wraps uuid4() function."""
    return uuid.uuid4()
