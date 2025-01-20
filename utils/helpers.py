import uuid
from datetime import datetime
from utils.enums import NoteStatus


def str_to_date(str_date, is_deadline=True):
    try:
        date = datetime.strptime(str_date, "%d-%m-%Y %H:%M")
        if is_deadline and date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date
    except ValueError as e:
        raise e


def date_to_str(date, is_deadline, state=NoteStatus.TERMLESS):
    if not is_deadline or state not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
        return datetime.strftime(date, "%B %d, %Y %H:%M")
    else:
        return "NO DEADLINE"


def generate_id():
    return uuid.uuid4()