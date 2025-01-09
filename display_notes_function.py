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
    date_display_fmt: str = "%B %d, %Y %H:%M"
    print (
        f"\n\n{Fore.CYAN}Note ID #{Style.RESET_ALL}{note["id"]}\n\n"
        f"{Fore.GREEN}Username: {Style.RESET_ALL}{note["username"]}\n"
        f"{"\n".join(Fore.YELLOW + "Title " + str(i + 1) + ": " + Style.RESET_ALL + title for i, title in enumerate(note["titles"]))}\n"
        f"{Fore.MAGENTA}Content: \n{Style.RESET_ALL}{note["content"].replace('{{', '').replace('}}', '')}\n\n"
        f"{Fore.BLUE}Status: {Style.RESET_ALL}{note["status"].name}\n"
        f"{Fore.RED}Created: {Style.RESET_ALL}{datetime.strftime(note["created_date"], date_display_fmt)}\n"
        f"{Fore.RED}Deadline: {Style.RESET_ALL}{datetime.strftime(note["issue_date"], date_display_fmt)
        if note["status"] != Status.TERMLESS else "no deadline"}\n"
    )

def display_note_short(note):
    print (f"{Fore.CYAN}Note ID #{Style.RESET_ALL}{note["id"]}: {note["titles"][0]}\n\n")


def display_notes(notes_list, params = None):
    if len(notes_list) < 1:
        print("No notes yet\n")
    else:
        notes_sorted = sorted(notes_list, key=lambda x: x["created_date"]) if params[1] == 'c' else (
            sorted(notes_list, key=lambda x: (x["issue_date"] == datetime.min, x["issue_date"]), reverse=True))
        for n in notes_sorted:
            display_note_full(n) if params[0] == 'y' else display_note_short(n)
            print("-" * 30)


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