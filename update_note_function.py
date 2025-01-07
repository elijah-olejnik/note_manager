# note status as Enum for convenience
import json
from datetime import datetime
from enum import Enum


class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3


# The JSON decoder function
def note_decoder(obj):
    obj["status"] = Status[obj["status"]]
    obj["created_date"] = datetime.fromisoformat(obj["created_date"])
    try:
        obj["issue_date"] = datetime.fromisoformat(obj["issue_date"])
    except ValueError:
        pass
    return obj


def load_from_json() -> dict:
    try:
        with open("notes.json") as f:
            import_list = json.loads(f.read(), object_hook=note_decoder)
            return import_list[0]
    except (OSError, ValueError) as e:
        print("Couldn't open/read notes.json:", e)

def update_note(note):
