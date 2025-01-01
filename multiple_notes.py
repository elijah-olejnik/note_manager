from datetime import datetime
from enum import Enum
import re

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3

class NoteManager:
    _in_date_fmt = "%d-%m-%Y"
    _out_date_fmt = "%A %d %B"
    _regexp = r'\{\{(.*?)\}\}'
    _prompts = (
        'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                           'titles/headers within your text,\nuse double curly braces, e.g. {{Some title}}',
        'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED, "p" if POSTPONED '
        'or skip pressing Enter if TERMLESS',
        'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
        'Enter the note deadline date in "dd-mm-yyyy" format or press Enter if termless'
    )

    def __init__(self):
        self._notes = []

    def _is_date_accepted(self, str_date = "", is_issue_date = False):
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

    def _add_from_console(self):
        note = {
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
                                   + (f" (today is {datetime.strftime(datetime.today(), self._in_date_fmt)}): "
                                   if i == 3 else ": "))
                if i < 2 and not user_input:
                    continue
                match i:
                    case 0:
                        note["username"] = user_input
                    case 1:
                        headers = re.findall(self._regexp, user_input)
                        if headers:
                            note["titles"] = headers
                            note["content"] = re.sub(self._regexp, r'\n\n\1\n\n', user_input)
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

    def print_all_to_console(self):
        print(self.__str__())

    def interact_with_console(self):
        print("\n", "Welcome to the note manager!\n")
        while True:
            command = input("Enter 'n' for a new note or 'q' for quit: ")
            match command:
                case 'q':
                    break
                case 'n':
                    self._add_from_console()
                case _:
                    print(f"{command} is not a command")
                    continue
        print("\nHere is your notes:\n")
        print(self.__str__())

    def __str__(self):
        output_string = ""
        for note in self._notes:
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
        return output_string

note_manager = NoteManager()
note_manager.interact_with_console()