import curses
import json
from datetime import datetime
from enum import Enum
from typing import Tuple, Union
import femto

date_fmts = ("%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


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


def user_confirmation():
    while True:
        user_input = input("Are you sure? y|n: ")
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            pass


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
        

def str_to_date(str_date="") -> Tuple[bool, Union[datetime, ValueError]]:
    for fmt in date_fmts:
        try:
            date = datetime.strptime(str_date, fmt)
            if date < datetime.now():
                raise ValueError("\nThe deadline can be only in the future. Try Again.\n")
            return True, date
        except ValueError as e:
            return False, e


def get_value_from_console(input_type, prompt = "", enum_ = Status):
    while True:
        user_input = input(prompt) if input_type != InputType.TEXT else curses.wrapper(femto.femto, prompt)
        if input_type == InputType.ENUM_VALUE:
            if not user_input.isdigit():
                name = user_input.upper()
                if name not in (item.name for item in enum_):
                    display_error_message()
                    continue
                return enum_[name]
            else:
                value = int(user_input)
                if value not in (item.value for item in enum_):
                    display_error_message()
                    continue
                return enum_(value)
        elif input_type == InputType.DATE:
            date = str_to_date(user_input)
            if not date[0]:
                print(date[1])
                continue
            return date[1]
        else:
            if not user_input:
                display_error_message()
                continue
            return user_input


def update_note(note):
    while True:
        print(
            "\nChoose what to update or quit program:\n"
            "1 - Username\n"
            "2 - Title\n"
            "3 - Content\n"
            "4 - Status\n"
            "5 - Deadline\n"
            "6 - Quit"
        )
        command = input("\nEnter your choice: ")
        match command:
            case '1':
                input_value = get_value_from_console(InputType.STRING, "Enter new username: ")
                if not user_confirmation():
                    continue
                note["username"] = input_value
                print("Note updated:\n\n", note)
            case '2':
                input_value = get_value_from_console(InputType.STRING, "Enter new title: ")
                if not user_confirmation():
                    continue
                note["title"] = input_value
                print("Note updated:\n\n", note)
            case '3':
                input_value = get_value_from_console(InputType.TEXT, note["content"])
                if not user_confirmation():
                    continue
                note["content"] = input_value
                print("Note updated:\n\n", note)
            case '4':
                print(
                    "Choose the new note state:\n"
                    "0 or active\n"
                    "1 or completed\n"
                    "2 or termless\n"
                    "3 or postponed\n"
                )
                input_value = get_value_from_console(InputType.ENUM_VALUE, "\nEnter a word or a number: ")
                if not user_confirmation():
                    continue
                note["status"] = input_value
                print("Note updated:\n\n", note)
            case '5':
                input_value = get_value_from_console(InputType.DATE, "Enter new deadline date: ")
                if not user_confirmation():
                    continue
                note["issue_date"] = input_value
                print("Note updated:\n\n", note)
            case '6':
                break
            case _:
                display_error_message()
        
        
def main():
    note = load_from_json()
    print("The current note:\n\n", note)
    update_note(note)
    return 0


if __name__ == "__main__":
    main()
