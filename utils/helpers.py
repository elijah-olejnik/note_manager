import uuid
from datetime import datetime
from utils.enums import NoteStatus
from interface import strings


def str_to_date(str_date, is_deadline=True):
    try:
        date = datetime.strptime(str_date, "%d-%m-%Y %H:%M")
        if is_deadline and date <= (datetime.now()):
            raise ValueError(strings.deadline_invalid_str)
        return date
    except ValueError as e:
        raise e


def date_to_str(date, is_deadline, state=NoteStatus.TERMLESS):
    if not is_deadline or state not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
        return datetime.strftime(date, "%B %d, %Y %H:%M")
    else:
        return strings.no_deadline_str


def input_to_enum_value(input_str, enum_class):
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
    return uuid.uuid4()