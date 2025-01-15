import curses
import random
from pathlib import Path

import yaml
from datetime import datetime
from enum import Enum
from femto import femto  # My tiny console editor


notes = []
datetime_fmt = "%d-%m-%Y %H:%M"


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


class InputType(Enum):
    INT = 0
    STR = 1
    TEXT = 2
    ENUM_VAL = 3
    DATE = 4


class DataIntegrityError(Exception):
    pass


def str_to_deadline(str_date):
    try:
        date = datetime.strptime(str_date, datetime_fmt)
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date
    except ValueError as e:
        raise e


def get_value_from_console(input_type, prompt="", enum_=None):
    while True:
        try:
            user_input = input(prompt).strip() if input_type != InputType.TEXT else curses.wrapper(femto, prompt)
            if not user_input and input_type != InputType.DATE:
                continue
            match input_type:
                case InputType.INT:
                    return int(user_input)
                case InputType.ENUM_VAL:
                    if not user_input.isdigit():
                        name = user_input.upper().strip()
                        return enum_[name]
                    else:
                        value = int(user_input.strip())
                        return enum_(value)
                case InputType.DATE:
                    return str_to_deadline(user_input)
                case _:
                    return user_input
        except (KeyError, ValueError) as e:
            print('\n', e, '\n')


def state_submenu():
    print(
        "\nChoose the new note state:\n\n"
        "0 or active\n"
        "1 or completed\n"
        "2 or postponed\n"
        "3 or termless\n"
    )
    return get_value_from_console(InputType.ENUM_VAL, "Enter a word or a number: ", NoteStatus)


def create_note():
    note = {
        "username" : "Enter a username: ",
        "title" : "Enter a title: ",
        "content" : "",
        "status" : "Enter the note state",
        "issue_date" : "Enter note deadline (dd-mm-yyyy hh:mm): "
    }
    for key, value in note.items():
        match key:
            case "content":
                note[key] = get_value_from_console(InputType.TEXT)
            case "status":
                note[key] = state_submenu()
            case ("issue_date"):
                if note["status"] in (NoteStatus.COMPLETED, NoteStatus.TERMLESS):
                    note[key] = datetime.min
                else:
                    note[key] = get_value_from_console(InputType.DATE, value)
            case _:
                note[key] = get_value_from_console(InputType.STR, value).strip()
    note["id_"] = random.randint(10000, 99999)
    note["created_date"] = datetime.now()
    return note


def datetime_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())


def enum_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)


def save_notes_to_file(note_list, filename):
    if not note_list:
        return "No notes to save. Create a note first"
    try:
        with open(filename, 'w') as file:
            yaml.dump(note_list, file)
        return "Notes are successfully saved"
    except (OSError, ValueError) as e:
        return e.__str__()


def load_notes_from_file(filename):
    required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
    try:
        with open(filename, 'r') as file:
            import_list = yaml.safe_load(file)
        if not import_list:
            raise ValueError(f"File {filename} is empty! You should create and save notes first.")
        note_list = []
        for dic in import_list:
            if not all(field in dic for field in required_fields):
                raise DataIntegrityError(f"Missing required fields in record: {dic}\nCheck file content")
            try:
                note = {
                    "content" : dic["content"],
                    "created_date" : datetime.fromisoformat(dic["created_date"]),
                    "id_" : dic["id_"],
                    "issue_date" : datetime.fromisoformat(dic["issue_date"]),
                    "status" : NoteStatus[dic["status"]],
                    "title" : dic["title"],
                    "username" : dic["username"]
                }
                note_list.append(note)
            except (ValueError, KeyError, TypeError) as e:
                raise DataIntegrityError(f"Data format error in record {dic}: {e}\nCheck file content.")
        return note_list
    except (OSError, ValueError, yaml.YAMLError, DataIntegrityError) as e:
        print("\nNotes load failed:", e)
        return []


def main_menu():
    if notes:
        print(
            "\n1. Create note\n"
            "2. Save notes and quit\n"
            "3. Quit without saving\n"
        )
    else:
        print(
            "\n1. Create note\n"
            "2. Quit\n"
        )
    return get_value_from_console(InputType, "Enter your choice: ")


def archive_check(pathname):
    archive = Path(pathname)
    if archive.is_file():
        return True
    return False


def main():
    yaml.add_representer(datetime, datetime_representer)
    yaml.add_representer(NoteStatus, enum_representer)
    file_name = "notes_stage_4.yaml"
    file_path = Path(file_name)
    global notes
    if not file_path.is_file():
        try:
            with open(file_name, 'w'): pass
        except (OSError, ValueError) as e:
            print("Can't create a new file:", e)
        print(f"File {file_path} wasn't found. A new file is created.")
    else:
        notes = load_notes_from_file(file_path)
    if notes:
        print('\n', notes)
    while True:
        choice = main_menu()
        if choice == '3':
            break
        elif choice == '2':
            if notes:
                print('\n', save_notes_to_file(notes, file_name))
            break
        elif choice == '1':
            notes.append(create_note())
            print("Note added\n\n", notes)


if __name__ == "__main__":
    main()