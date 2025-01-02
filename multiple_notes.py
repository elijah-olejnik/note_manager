import random
from datetime import datetime
from enum import Enum
import re
from typing import Tuple, Union
import json

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

class NoteManager:
    _in_date_fmt = "%d-%m-%Y"
    _out_date_fmt = "%B %d, %Y"
    _regexp = r'\{\{(.*?)\}\}'
    _prompts = (
        'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                           'titles/headers within your text,\nuse double curly braces, e.g. {{Some title}}.'
                           '\nUse Enter key to add a new line,\nor type "end" to finish the note input\n',
        'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED, "p" if POSTPONED '
        'or skip pressing Enter if TERMLESS',
        'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
        'Enter the note deadline date in "dd-mm-yyyy" format or press Enter if termless'
    )

    def __init__(self):
        self._notes = []

    def has_notes(self):
        if len(self._notes) < 1:
            return False
        return True

    def _is_date_accepted(self, str_date = "", is_issue_date = False) -> Tuple[bool, Union[datetime, ValueError]]:
        try:
            date = datetime.strptime(str_date, self._in_date_fmt)
            if is_issue_date:
                return True, date
            else:
                if date.date() != datetime.today().date():
                    print("\nWhat are you hiding, cheater? =)")
                return True, date
        except ValueError as e:
            return False, e

    def add_from_console(self):
        id_ = random.randint(0000, 9999)
        note = {
            "id" : id_,
            "username": "",
            "titles": [],
            "content" : "",
            "status" : Status.TERMLESS,
            "created_date" : datetime.now(),
            "issue_date" : "Termless"
        }
        for i, prompt in enumerate(self._prompts):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(note["created_date"], self._in_date_fmt)}): "
                                   if i == 3 else ": "))
                if i < 2 and not user_input:
                    continue
                match i:
                    case 0:
                        note["username"] = user_input
                    case 1:
                        while True:
                            new_line = input()
                            if new_line.lower() == "end":
                                break
                            user_input += "\n" + new_line
                        headers = re.findall(self._regexp, user_input)
                        if headers:
                            note["titles"] = headers
                            note["content"] = re.sub(self._regexp, r'\n\1\n', user_input)
                        else:
                            note["content"] = user_input
                            words = user_input.split()
                            if len(words) == 1:
                                note["titles"].append(words[0])
                            elif len(words) == 2:
                                note["titles"].append(" ".join(words[:2]))
                            else:
                                note["titles"].append(" ".join(words[:3]))
                    case 2:
                        match user_input:
                            case 'a':
                                note["status"] = Status.ACTIVE
                            case 'c':
                                note["status"] = Status.COMPLETED
                            case 'p':
                                note["status"] = Status.POSTPONED
                            case _:
                                note["status"] = Status.TERMLESS
                    case _:
                        if not user_input:
                            break
                        result = self._is_date_accepted(user_input, i == 4)
                        if result[0]:
                            if i == 3:
                                note["created_date"] = result[1]
                            elif i == 4:
                                if result[1] < note.get("created_date"):
                                    print("\nThe deadline date of a note can't be "
                                                     "earlier than the date it was created!")
                                    continue
                                note["issue_date"] = result[1]
                        else:
                            print("\n", result[1])
                            continue
                break
        self._notes.append(note)
        print("\nYour note is successfully saved\n")

    def __str__(self):
        output_string = ""
        for i, note in enumerate(self._notes):
            output_string += f"\n\nNote ID #{note["id"]}\n\n"
            for key, value in note.items():
                match key:
                    case "titles":
                        output_string += "\n".join(
                            key.capitalize()[:-1] + " " + str(x + 1) + ": " + str(t) for x, t in enumerate(value)
                        ) + "\n"
                    case "content":
                        output_string += "\n" + key.capitalize() + ":" + "\n" + value + "\n\n"
                    case "status":
                        output_string += key.capitalize() + ": " + value.name + "\n"
                    case "created_date":
                        output_string += key.capitalize() + ": " + datetime.strftime(value, self._out_date_fmt) + "\n"
                    case "issue_date":
                        output_string += key.capitalize() + ": " + (
                            datetime.strftime(value, self._out_date_fmt)
                            if isinstance(value, datetime) else value
                        )
                    case _:
                        output_string += key.capitalize() + ": " + value + "\n"
            output_string += "\n" + "_" * 30
        return output_string

    def get_all_notes_as_str(self):
        return self.__str__()

    def delete_note(self, key):
        if key.isdigit():
            id_ = int(key)
            for i, note in enumerate(self._notes):
                if note["id"] == id_:
                    self._notes.pop(i)
                    return True
        else:
            for i, note in enumerate(self._notes):
                if key in note["titles"][0]:
                    self._notes.pop(i)
                    return True
        return False

    # def is_json_saved(self):
    #     if not self.has_notes():
    #         return False
    #     try:
    #         with open("notes.json", 'w') as file_:
    #             file_.write(json.dumps(self._notes, cls = NoteEncoder, indent = 4))
    #         return True
    #     except (ValueError, OSError):
    #         return False

note_manager = NoteManager()

print("\n", "Welcome to the note manager!\n")
while True:
    command = input("Enter 'n' for a new note, 'd' to delete one or 'q' for quit: ")
    match command:
        case 'q':
            break
        case 'd':
            if not note_manager.has_notes():
                print("\nNo notes yet")
                continue
            print("\nHere are your notes:", note_manager.get_all_notes_as_str())
            while True:
                user_key = input("Enter an ID or the title of the note to delete: ")
                if not note_manager.delete_note(user_key):
                    print(f"The note {user_key} not found!")
                    continue
                print(f"\nThe note {user_key} is successfully deleted")
        case 'n':
            note_manager.add_from_console()
        case _:
            print(f"{command} is not a command")
            continue

print("\nHere are your notes:", note_manager.get_all_notes_as_str())

# if note_manager.is_json_saved():
#     print("File saved")