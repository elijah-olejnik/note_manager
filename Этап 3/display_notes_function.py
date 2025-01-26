import sys
from datetime import datetime
from enum import Enum
import json
import colorama
from colorama import Fore, Style


# note status as Enum for convenience
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
        return obj
    return obj


def load_from_json():
    try:
        with open("notes.json") as f:
            import_list = json.loads(f.read(), object_hook=note_decoder)
            return import_list
    except (OSError, ValueError) as e:
        print("\nCouldn't open/read notes.json:", e)
        return []


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
    print (f"{Fore.CYAN}Note ID #{Style.RESET_ALL}{note["id"]}: {note["titles"][0]}\n\n")


def display_notes(notes_list, params=None, per_page=3):
    if len(notes_list) < 1:
        print("No notes yet\n")
        return
    if not params:
        params = ['y', 'c']
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


def main():
    notes = []
    colorama.init(autoreset=True)
    display_notes(notes)
    decision = input("Load from JSON? y|n: ")
    if decision != 'y':
        print("quitting...")
        sys.exit(0)
    print("Choose parameters:\nDisplay all note data? y|n\nSort by creation date or deadline? c|d")
    while True:
        params = input("Enter parameters separated by ; e.g.: y;c: ").split(';')
        if params[0] not in ('y','n') or params[1] not in ('c','d'):
            continue
        display_notes(load_from_json(), params)
        break
    return 0


if __name__ == "__main__":
    main()