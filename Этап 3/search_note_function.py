import json
from datetime import datetime
from enum import Enum
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


def display_notes(notes_list, per_page=3):
    if len(notes_list) < 1:
        print("No notes yet\n")
        return
    total_notes = len(notes_list)
    page = 0
    while True:
        start_index = page * per_page
        end_index = start_index + per_page
        notes_to_display = notes_list[start_index:end_index]
        for n in notes_to_display:
            display_note_full(n)
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
    filtered_notes = []
    for note in notes:
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
            filtered_notes.append(note)
    return filtered_notes


def main():
    colorama.init(autoreset=True)
    notes = load_from_json()
    print("\n", notes)
    while True:
        command = input(
            "\nSearch by:\n"
            "s - state\n"
            "k - keywords\n"
            "m - both\n"
            "q - quit\n\n"
            "Enter your command: "
        )
        if command == 'q':
            break
        keywords = None
        if command in ('k', 'm'):
            keywords = [key.strip().lower() for key in input("Enter keywords, separated by ; : ").split(';')]
        state = None
        if command in ('s', 'm'):
            while True:
                try:
                    user_input = int(input(
                        "\nChoose the note state:\n"
                        "0 - for active\n"
                        "1 - for completed\n"
                        "2 - for termless\n"
                        "3 - for postponed\n\n"
                        "Enter the number: "
                    ))
                    if user_input not in range(0, 4):
                        raise ValueError("The number is not in range")
                    state = Status(user_input)
                    break
                except ValueError as e:
                    print("\n", e)
                    continue
        notes_found = search_notes(notes, keywords, state)
        if len(notes_found) < 1:
            print("\nNo matches found\n")
            continue
        display_notes(notes_found)
    return 0


if __name__ == "__main__":
    main()