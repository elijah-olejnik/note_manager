import uuid
from datetime import datetime


def str_to_deadline(str_date):
    try:
        date = datetime.strptime(str_date, "%d-%m-%Y %H:%M")
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date
    except ValueError as e:
        raise e


def generate_id():
    return uuid.uuid4()