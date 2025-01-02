import json
import sys
from datetime import datetime
from enum import Enum

out_date_fmt = "%B %d, %Y"


class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3


class NoteEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        elif isinstance(o, datetime):
            return o.isoformat()
        else:
            return o


def custom_decoder(obj):
    obj["status"] = Status[obj["status"]]
    obj["created_date"] = datetime.fromisoformat(obj["created_date"])
    try:
        obj["issue_date"] = datetime.fromisoformat(obj["issue_date"])
    except ValueError:
        pass
    return obj


def load_notes():
    notes_list = []
    try:
        with open("notes.json") as f:
            notes_list = json.loads(f.read(), object_hook=custom_decoder)
    except (OSError, ValueError) as e:
        print("Couldn't open/read notes.json:", e)
        sys.exit(1)
    return notes_list


notes = load_notes()


def format_output():
    output_string = ""
    for i, note in enumerate(notes):
        output_string += f"\n\nNote ID #{note["id"]}\n"
        for key, value in note.items():
            match key:
                case "id":
                    continue
                case "titles":
                    output_string += "\n".join(
                        key.capitalize()[:-1] + " " + str(x + 1) + ": " + str(t) for x, t in enumerate(value)
                    ) + "\n"
                case "content":
                    output_string += "\n" + key.capitalize() + ":" + "\n" + value + "\n\n"
                case "status":
                    output_string += key.capitalize() + ": " + value.name + "\n"
                case "created_date":
                    output_string += key.capitalize() + ": " + datetime.strftime(value, out_date_fmt) + "\n"
                case "issue_date":
                    output_string += key.capitalize() + ": " + (
                        datetime.strftime(value, out_date_fmt)
                        if isinstance(value, datetime) else value
                    )
                case _:
                    output_string += key.capitalize() + ": " + value + "\n"
        output_string += "\n" + "_" * 30
    return output_string


def delete_notes(indexes):
    for i in sorted(indexes, reverse = True):
        del notes[i]


def search_notes(keys):
    notes_found = set()
    for i, note in enumerate(notes):
        for key in keys:
            if key[0] == " ":
                ey = key[1:]
                key = ey
            if key.lower() in note["username"].lower():
                notes_found.add(i)
            elif key.lower() in note["titles"][0].lower():
                notes_found.add(i)
    if len(notes_found) > 0:
        return True, notes_found
    else:
        return False, notes_found


print("\nHere are the notes:", format_output())

while True:
    user_keys = input("Enter a username or title separated by ';'\neach for one note to delete : ").split(';')
    result = search_notes(user_keys)
    if not result[0]:
        print("\nNot a single note found by your keyword")
        continue
    print(f"\nFound notes: {len(result[1])}")
    while True:
        user_input = input("Delete? (yes, no): ")
        if user_input not in ('yes', 'no'):
            continue
        elif user_input == "yes":
            delete_notes(result[1])
            print("\nSuccessfully deleted\n")
        break
    break

print("\nNotes remained:", len(notes), format_output())
