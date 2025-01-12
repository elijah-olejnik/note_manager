import random
from datetime import datetime, timedelta
from enum import Enum
from colorama import Style, Fore
import curses
import femto
import json
import colorama


date_fmts = ("%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


class InputType(Enum):
    INT = 0
    STR = 1
    TEXT = 2
    ENUM_VAL = 3
    DATE = 4


class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


class NoteEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj


def note_decoder(obj):
    obj["status"] = Status[obj["status"]]
    obj["created_date"] = datetime.fromisoformat(obj["created_date"])
    obj["issue_date"] = datetime.fromisoformat(obj["issue_date"])
    return obj


def user_confirmation():
    while True:
        user_input = input("Are you sure? y|n: ")
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            pass


def load_from_json(file_str = "notes.json"):
    try:
        with open(file_str) as f:
            import_list = json.loads(f.read(), object_hook=note_decoder)
            return import_list
    except (OSError, ValueError) as er:
        print("\nCouldn't open/read notes.json:", er)
        return []


def save_to_json(notes):
    try:
        with open("notes.json", 'w') as file_:
            file_.write(json.dumps(notes, cls=NoteEncoder, indent=4))
    except (ValueError, OSError) as e:
        print("The note manager can't save changes:", e)


def str_to_deadline(str_date):
    if not str_date:
        return datetime.now() + timedelta(weeks=1)
    last_error = None
    for fmt in date_fmts:
        try:
            date = datetime.strptime(str_date, fmt)
            if date < (datetime.now() + timedelta(days=1)):
                raise ValueError("The deadline can be only in the future.")
            return date
        except ValueError as err:
            last_error = err
    if last_error:
        raise ValueError(f"Date format should be one of {date_fmts}.") from last_error


def get_value_from_console(input_type, prompt = "", enum_ = None):
    while True:
        try:
            user_input = input(prompt) if input_type != InputType.TEXT else curses.wrapper(femto.femto, prompt)
            if not user_input and InputType != InputType.DATE:
                continue
            match input_type:
                case InputType.INT:
                    return int(user_input)
                case InputType.ENUM_VAL:
                    if not user_input.isdigit():
                        name = user_input.upper()
                        return enum_[name]
                    else:
                        value = int(user_input)
                        return enum_(value)
                case InputType.DATE:
                    return str_to_deadline(user_input)
                case _:
                    return user_input
        except (KeyError, ValueError) as e:
            print('\n', e)


def create_note(notes):
    note = {
        "id" : random.randint(10000, 99999),
        "username" : ["", "Enter your name: "],
        "title" : ["", "Enter the note title: "],
        "content" : "",
        "status" : [
            Status.TERMLESS,
            "Enter the note state\n"
            "0 or active\n"
            "1 or completed\n"
            "2 or postponed\n"
            "3 or termless\n\n"
            "State: "
        ],
        "created_date" : datetime.now(),
        "issue_date" : [
            datetime.min,
            "Enter the deadline date (dd-mm-yyyy)\n"
            "or press Enter to leave the default value (1 week): "
        ]
    }
    for key, value in note.items():
        match key:
            case "id" | "created_date":
                continue
            case "content":
                note[key] = get_value_from_console(InputType.TEXT)
            case "status":
                note[key] = get_value_from_console(InputType.ENUM_VAL, value[1], Status)
            case "issue_date":
                note[key] = get_value_from_console(InputType.DATE, value[1])
            case _:
                note[key] = get_value_from_console(InputType.STR, value[1])
    notes.append(note)
    save_to_json(notes)
    print("\nNote created:\n")
    display_note_full(note)


def update_note(notes, i):
    while True:
        print(
            "\nChoose what to update or quit program:\n"
            "1 - Username\n"
            "2 - Title\n"
            "3 - Content\n"
            "4 - Status\n"
            "5 - Deadline\n"
            "6 - Return to the main menu\n"
        )
        command = get_value_from_console(InputType.INT, "Enter your choice: ")
        match command:
            case 1:
                input_value = get_value_from_console(InputType.STR, "Enter new username: ")
                if not user_confirmation():
                    continue
                notes[i]["username"] = input_value
            case 2:
                input_value = get_value_from_console(InputType.STR, "Enter new title: ")
                if not user_confirmation():
                    continue
                notes[i]["title"] = input_value
            case 3:
                input_value = get_value_from_console(InputType.TEXT, notes[i]["content"])
                if not user_confirmation():
                    continue
                notes[i]["content"] = input_value
            case 4:
                print(
                    "Choose the new note state:\n"
                    "0 or active\n"
                    "1 or completed\n"
                    "2 or postponed\n"
                    "3 or termless\n"
                )
                input_value = get_value_from_console(InputType.ENUM_VAL, "\nEnter a word or a number: ")
                if not user_confirmation():
                    continue
                notes[i]["status"] = input_value
            case 5:
                input_value = get_value_from_console(InputType.DATE, "Enter new deadline date: ")
                if not user_confirmation():
                    continue
                notes[i]["issue_date"] = input_value
            case 6:
                break
            case _:
                continue
        save_to_json(notes)
        print("Note updated:\n")
        display_note_full(notes[i])


def display_note_full(note):
    row_format = "{:<20} | {:<60}"
    print("-" * 77)
    print(row_format.format(Fore.CYAN + "Note ID" + Style.RESET_ALL, note["id"]))
    print(row_format.format(Fore.GREEN + "Username" + Style.RESET_ALL, note["username"]))
    for i, title in enumerate(note["titles"]):
        print(row_format.format(f"{Fore.YELLOW}Title {i}{Style.RESET_ALL}", title))
    content = "\n" + note["content"].replace("{{", "").replace("}}", "")
    print(row_format.format(Fore.MAGENTA + "Content" + Style.RESET_ALL, content))
    print(row_format.format(Fore.BLUE + "Status" + Style.RESET_ALL, note["status"].name))
    date_display_fmt = "%B %d, %Y %H:%M"
    created = datetime.strftime(note["created_date"], date_display_fmt)
    print(row_format.format(Fore.RED + "Created" + Style.RESET_ALL, created))
    if note["status"] != Status.TERMLESS:
        deadline = datetime.strftime(note["issue_date"], date_display_fmt)
    else:
        deadline = Status.TERMLESS.name
    print(row_format.format(Fore.RED + "Deadline" + Style.RESET_ALL, deadline))
    print("-" * 77)


def display_note_short(note):
    print(f"{Fore.CYAN}Note ID #{Style.RESET_ALL}{note["id"]}: {note["titles"][0]}\n\n")


def display_notes(notes_list, params=None, per_page=3):
    if len(notes_list) < 1:
        print("No notes yet\n")
        return
    notes_sorted = sorted(notes_list, key=lambda x: x["created_date"]) if params[1] == 'c' else (
        sorted(notes_list, key=lambda x: (x["issue_date"] == datetime.min, x["issue_date"]), reverse=True)
    )
    total_notes = len(notes_sorted)
    page = 0
    while True:
        start_index = page * per_page
        end_index = start_index + per_page
        notes_to_display = notes_sorted[start_index:end_index]
        for n in notes_to_display:
            display_note_full(n) if params[0] == 'y' else display_note_short(n)
        print(f"Page {page + 1} of {(total_notes + per_page - 1) // per_page}")
        print("n - next page, p - previous page, q - quit")
        choice = input("Enter choice: ").lower()
        if choice == 'n':
            if end_index < total_notes:
                page += 1
            else:
                print("You are on the last page.")
        elif choice == 'p':
            if start_index > 0:
                page -= 1
            else:
                print("You are on the first page.")
        elif choice == 'q':
            break
        else:
            print("Invalid choice. Please enter 'n', 'p', or 'q'.")


def search_notes(notes, keys=None, state=None):
    if not notes:
        print("No notes yet!")
        return []
    filtered_indexes = []
    for i, note in enumerate(notes):
        status_match = (state is None or note["status"] == state)
        keyword_match = False
        if keys:
            for key in keys:
                key = key.strip().lower()
                if (key.isdigit() and key == str(note["id"])) or \
                   (key in note["username"].lower()) or \
                   any(key in title.lower() for title in note["titles"]) or \
                   (key in note["content"].lower()):
                    keyword_match = True
                    break
        else:
            keyword_match = True
        if status_match and keyword_match:
            filtered_indexes.append(i)
    return filtered_indexes


def main_menu(notes):
    while True:
        print(
            "\nMain menu:\n"
            "1. Create note\n"
            "2. Show all notes\n"
            "3. Update note\n"
            "4. Delete note\n"
            "5. Search notes\n"
            "6. Quit app\n"
        )
        try:
            choice = get_value_from_console(InputType.INT, "Enter your choice: ")
            match choice:
                case 1:
                    create_note(notes)
                case 2:
                    print(
                        "Display all note data? y|n\n"
                        "Sort by creation date or deadline? c|d\n"
                    )
                    while True:
                        params = (get_value_from_console(
                            InputType.STR,
                            "Enter parameters separated by ;\n"
                            "e.g.: y;c\n"
                            "or enter b to get back to the main menu: "
                        ).split(';'))
                        if params[0] == 'b':
                            break
                        elif params[0] not in ('y', 'n') or params[1] not in ('c', 'd'):
                            continue
                        display_notes(notes, params)
                        break
                case 3:
                    while True:
                        note_id = get_value_from_console(InputType.INT, "Enter the note ID to edit: ")
                        found = search_notes(notes, note_id)
                        if len(found) < 1:
                            print(f"\nNo notes found by ID #{note_id}.\n")
                            continue
                        update_note(notes, found[0])
                        break
                case 4:
                    while True:
                        note_id = get_value_from_console(InputType.INT, "Enter the note ID to delete: ")
                        found = search_notes(notes, note_id)
                        if len(found) < 1:
                            print(f"\nNo notes found by ID #{note_id}.\n")
                            continue
                        del notes[found[0]]
                        break
                case 5:
                    while True:
                        command = get_value_from_console(
                            InputType.INT,
                            "\nSearch by:\n"
                            "1 - state\n"
                            "2 - keywords\n"
                            "3 - both\n"
                            "4 - Back to the main menu\n\n"
                            "Enter your choice: "
                        )
                        if command == 4:
                            break
                        keywords = None
                        if command in (2, 3):
                            keywords = [key.strip().lower() for key in
                                        input("Enter keywords, separated by ; : ").split(';')]
                        state = None
                        if command in (1, 3):
                            print(
                                "Choose the new note state:\n"
                                "0 or active\n"
                                "1 or completed\n"
                                "2 or postponed\n"
                                "3 or termless\n"
                            )
                            state = get_value_from_console(
                                InputType.ENUM_VAL,
                                "\nEnter a word or a number: ",
                                Status
                            )
                        found = search_notes(notes, keywords, state)
                        if len(found) < 1:
                            print("\nNo matches found\n")
                            continue
                        for i in found:
                            display_note_full(notes[i])
                case 6:
                    break
                case _:
                    raise
        except ValueError as e:
            print("\n", e)


def main():
    colorama.init(autoreset=True)
    main_menu(load_from_json())
    return 0


if __name__ == "__main__":
    main()