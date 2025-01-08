import curses
import json
from datetime import datetime
from enum import Enum
import femto


# input type as Enum for convenience
class InputType(Enum):
    STRING = 0
    TEXT = 1
    ENUM_VALUE = 2
    DATE = 3


# note status as Enum for convenience
class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3


def display_error_message(msg = ""):
    print("\nIncorrect input. Try again\n" if not msg else msg)


# The JSON decoder function
def note_decoder(obj):
    obj["status"] = Status[obj["status"]]
    obj["created_date"] = datetime.fromisoformat(obj["created_date"])
    try:
        obj["issue_date"] = datetime.fromisoformat(obj["issue_date"])
    except ValueError:
        return obj
    return obj


def load_from_json() -> dict:
    try:
        with open("notes.json") as f:
            import_list = json.loads(f.read(), object_hook=note_decoder)
            return import_list[0]
    except (OSError, ValueError) as e:
        print("\nCouldn't open/read notes.json:", e)


def get_value_from_console(prompt, input_type, enum_ = Status):
    while True:
        user_input = input(prompt) if input_type != InputType.TEXT else curses.wrapper(femto.femto)
        if input_type == InputType.ENUM_VALUE:
            if not user_input.isdigit():
                name = user_input.upper()
                if name not in (item.name for item in enum_):
                    display_error_message()
                    continue
                return enum_[name]
            else:
                value = str(user_input)
                if value not in (item.value for item in enum_):
                    display_error_message()
                    continue
                return enum_(0)
        elif input_type == InputType.DATE:
            pass # TODO
        else:
            if not user_input:
                display_error_message()
                continue
            return user_input


def update_note(note):
    while True:
        print(
            "\nChoose what to update:\n"
            "1 - Username\n"
            "2 - Title\n"
            "3 - Content\n"
            "4 - Status\n"
            "5 - Deadline\n"
        )
        command = input("\nEnter your choice: ")
        match command:
            case '1':
                pass # TODO