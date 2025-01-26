from datetime import datetime
from enum import Enum
import re

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2

class Note:
    _in_date_fmt = "%d-%m-%Y"
    _out_date_fmt = "%A %d %B"
    _regexp = r'\{\{(.*?)\}\}'

    def __init__(self):
        self._note = {
            "username" : "",
            "titles" : [],
            "content" : "",
            "status" : Status.TERMLESS,
            "created_date" : datetime.today(),
            "issue_date" : "Termless"
        }

    def get_note(self):
        return self._note

    def set_note(self, note=None):
        if note is None:
            note = {}
        self._note = note

    def _is_date_accepted(self, str_date = "", is_issue_date = False):
        try:
            date = datetime.strptime(str_date, self._in_date_fmt)
            if is_issue_date:
                if date < self._note["created_date"]:
                    raise ValueError("The expiration date of a note can't be "
                                     "earlier than the date it was created")
                self._note["issue_date"] = date
                return True
            else:
                if date.date() != datetime.today().date():
                    print("\nWhat are you hiding, cheater? =)")
                self._note["created_date"] = date
                return True
        except ValueError as e:
            print(f"\n{e}")
            return False

    def fill_from_console(self):
        prompts = (
            'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                               'titles/headers within your text,\nuse double curly braces, e.g. {{Some title}}',
            'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED or skip pressing Enter if TERMLESS',
            'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
            'Enter the note expiration date in "dd-mm-yyyy" format or press Enter if termless'
        )
        for i, prompt in enumerate(prompts):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(datetime.today(), self._in_date_fmt)}): "
                                   if i == 3 else ": "))
                if i < 2 and not user_input:
                    continue
                match i:
                    case 0:
                        self._note["username"] = user_input
                    case 1:
                        headers = re.findall(self._regexp, user_input)
                        if headers:
                            self._note["titles"] = headers
                            self._note["content"] = re.sub(self._regexp, r'\n\n\1\n\n', user_input)
                        else:
                            self._note["content"] = user_input
                            words = user_input.split()
                            if len(words) == 1:
                                self._note["titles"] = words
                            elif len(words) == 2:
                                self._note["titles"].append(" ".join(words[:2]))
                            else:
                                self._note["titles"].append(" ".join(words[:3]))
                    case 2:
                        if user_input == 'a':
                            self._note["status"] = Status.ACTIVE
                        elif user_input == 'c':
                            self._note["status"] = Status.COMPLETED
                        else:
                            self._note["status"] = Status.TERMLESS
                    case _:
                        if not user_input:
                            if i == 3:
                                self._note["created_date"] = datetime.now()
                            break
                        if not self._is_date_accepted(user_input, i == 4):
                            continue
                break

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        output_string = ""
        for key, value in self._note.items():
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

new_note = Note()
new_note.fill_from_console()
new_note.show_to_console()