from datetime import datetime
from enum import Enum

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2

class Note:
    in_date_fmt = "%d-%m-%Y"
    out_date_fmt = "%A %d %B"
    title_marker = "~~"

    def __init__(self):
        self.note = {
            "username" : "",
            "titles" : [],
            "content" : "",
            "status" : Status.TERMLESS,
            "created_date" : datetime.today(),
            "issue_date" : "Termless"
        }

    def get_note(self):
        return self.note

    def set_note(self, note=None):
        if note is None:
            note = {}
        self.note = note

    def _is_date_accepted(self, str_date = "", is_issue_date = False):
        try:
            date = datetime.strptime(str_date, self.in_date_fmt)
            if is_issue_date:
                if date < self.note["created_date"]:
                    raise ValueError("The expiration date of a note can't be "
                                     "earlier than the date it was created")
                self.note["issue_date"] = date
                return True
            else:
                if date.date() != datetime.today().date():
                    print("\nWhat are you hiding, cheater? =)")
                self.note["created_date"] = date
                return True
        except ValueError as e:
            print(f"\n{e}")
            return False

    def fill_from_console(self):
        prompts = (
            'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                               'titles/headers within your text,\nuse double tilde, e.g. ~~Some title~~',
            'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED or skip pressing Enter if TERMLESS',
            'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
            'Enter the note expiration date in "dd-mm-yyyy" format or press Enter if termless'
        )
        for i, prompt in enumerate(prompts):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(datetime.today(), self.in_date_fmt)}): "
                                   if i == 3 else ": "))
                if i < 2 and not user_input:
                    continue
                match i:
                    case 0:
                        self.note["username"] = user_input
                    case 1:
                        if user_input.count(self.title_marker) > 1:
                            self.note["titles"] = user_input.split(self.title_marker)[1::2]
                            self.note["content"] = user_input.replace(self.title_marker, "\n\n")
                            break
                        self.note["content"] = user_input
                        if user_input.count(" ") > 0:
                            self.note["titles"].append(user_input.split(" ")[0] + " " + user_input.split(" ")[1])
                        else:
                            self.note["titles"].append(user_input)
                    case 2:
                        if user_input == 'a':
                            self.note["status"] = Status.ACTIVE
                        elif user_input == 'c':
                            self.note["status"] = Status.COMPLETED
                        else:
                            self.note["status"] = Status.TERMLESS
                    case _:
                        if not user_input:
                            if i == 3:
                                self.note["created_date"] = datetime.now()
                            break
                        if not self._is_date_accepted(user_input, i == 4):
                            continue
                break

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        output_string = ""
        for key, value in self.note.items():
            match key:
                case "titles":
                    output_string += "\n".join(
                        key.capitalize()[:-1] + " " + str(x + 1) + ": " + str(t) for x, t in enumerate(value)
                    ) + "\n"
                case "content":
                    "\n" + key.capitalize() + "\n\n" + value + "\n\n"
                case "status":
                    output_string += key.capitalize() + ": " + value.name + "\n"
                case "created_date":
                    output_string += key.capitalize() + ": " + datetime.strftime(value, self.out_date_fmt) + "\n"
                case "issue_date":
                    output_string += key.capitalize() + ": " + (
                        datetime.strftime(value, self.out_date_fmt)
                        if isinstance(value, datetime) else value
                    )
                case _:
                    output_string += key.capitalize() + ": " + value + "\n"
        return output_string

new_note = Note()
new_note.fill_from_console()
new_note.show_to_console()