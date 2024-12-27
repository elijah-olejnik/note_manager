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
        self.note = [
            "username",
            [],
            "content",
            Status.TERMLESS,
            datetime.today(),
            "Termless"
        ]

    def get_note(self):
        return self.note

    def set_note(self, some_note=None):
        if some_note is None:
            some_note = []
        self.note = some_note

    def _is_date_accepted(self, str_date = "", is_issue_date = False):
        try:
            date = datetime.strptime(str_date, self.in_date_fmt)
            if is_issue_date:
                if date < self.note[4]:
                    raise ValueError("The expiration date of a note can't be "
                                     "earlier than the date it was created")
                self.note[5] = date
                return True
            else:
                if date.date() != datetime.today().date():
                    print("\nWhat are you hiding, cheater? =)")
                self.note[4] = date
                return True
        except ValueError as e:
            print(f"\n{e}")
            return False

    def fill_from_console(self):
        prompts = (
            'Enter your name', 'Enter your note. If you want to add a title, or additional '
                               'titles/headers within your text, use double tilde, e.g. ~~Some title~~',
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
                        self.note[i] = user_input
                    case 1:
                        if user_input.count(self.title_marker) > 1:
                            self.note[i] = user_input.split(self.title_marker)[1::2]
                            self.note[i + 1] = user_input.replace(self.title_marker, "\n\n")
                            break
                        elif user_input.count(" ") > 0:
                            self.note[i].append(user_input.split(" ")[0] + " " + user_input.split(" ")[1])
                            self.note[i + 1] = user_input
                            break
                        else:
                            self.note[i].append(user_input)
                            self.note[i + 1] = user_input
                    case 2:
                        if user_input == 'a':
                            self.note[i + 1] = Status.ACTIVE
                        elif user_input == 'c':
                            self.note[i + 1] = Status.COMPLETED
                        else:
                            self.note[i + 1] = Status.TERMLESS
                    case _:
                        if not user_input:
                            if i == 3:
                                self.note[i + 1] = datetime.now()
                            break
                        if not self._is_date_accepted(user_input, i == 4):
                            continue
                break

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        output_string = ""
        for i, key in enumerate (("User name: ", "Title ", "Content: ", "Status: ", "Created: ", "Expired: ")):
            match i:
                case 0:
                    output_string += key + self.note[i] + "\n"
                case 1:
                    output_string += "\n".join(
                        key + str(x + 1) + ": " + str(t) for x, t in enumerate(self.note[i])
                    ) + "\n"
                case 2:
                    output_string += "\n" + key + "\n\n" + self.note[i] + "\n\n"
                case 3:
                    output_string += key + self.note[i].name + "\n"
                case 4:
                    output_string += key + datetime.strftime(self.note[i], self.out_date_fmt) + "\n"
                case 5:
                    output_string += key + (
                        datetime.strftime(self.note[i], self.out_date_fmt)
                        if isinstance(self.note[i], datetime) else self.note[i]
                    )
        return output_string

new_note = Note()
new_note.fill_from_console()
new_note.show_to_console()