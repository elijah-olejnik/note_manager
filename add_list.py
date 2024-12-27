from datetime import datetime
from enum import Enum

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1

class Note:
    in_date_fmt = "%d-%m-%Y"
    out_date_fmt = "%A %d %B"

    def __init__(self):
        self.username = None
        self.titles = []
        self.content = None
        self.status = None
        self.created_date = None
        self.issue_date = "Termless"

    def is_date_accepted(self, str_date = "", is_issue_date = False):
        try:
            date = datetime.strptime(str_date, self.in_date_fmt)
            if is_issue_date:
                if date < self.created_date:
                    raise ValueError("The expiration date of a note can't be "
                                     "earlier than the date it was created")
                self.issue_date = date
                return True
            else:
                if date.date() != datetime.today().date():
                    print("\nWhat are you hiding, cheater? =)")
                self.created_date = date
                return True
        except ValueError as e:
            print(f"\n{e}")
            return False

    def fill_from_console(self):
        prompt_list = ('Enter your name', 'Enter your note. If you want to add a title, or additional '
                       'titles/headers within your text, use double tilde, e.g. ~~Some title~~',
                       'Enter the note state: "a" if Active or "c" if Completed',
                       'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
                       'Enter the note expiration date in "dd-mm-yyyy" format or press Enter if termless')
        for i, prompt in enumerate(prompt_list):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(datetime.today(), self.in_date_fmt)}): "
                                   if i == 3 else ": "))
                if i < 3 and not user_input:
                    continue
                match i:
                    case 0:
                        self.username = user_input
                    case 1:
                        self.titles = user_input.split("~~")[1::2]
                        self.content = user_input.replace("~~", "\n\n")
                    case 2:
                        if user_input == 'a':
                            self.status = Status.ACTIVE
                        elif user_input == 'c':
                            self.status = Status.COMPLETED
                        else:
                            continue
                    case _:
                        if not user_input:
                            if i == 3:
                                self.created_date = datetime.now()
                            break
                        if not self.is_date_accepted(user_input, i == 4):
                            continue
                break

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        return (f"User name: {self.username}\n"
                f"{"\n".join("Title " + str(i + 1) + ": " + str(t) for i, t in enumerate(self.titles))}\n"
                f"Content:\n\n{self.content}\n\n"
                f"Status: {self.status.name}\n"
                f"Created: {datetime.strftime(self.created_date, self.out_date_fmt)}\n"
                f"Expired: {
                datetime.strftime(self.issue_date, self.out_date_fmt)
                if isinstance(self.issue_date, datetime)
                else self.issue_date}\n")

new_note = Note()
new_note.fill_from_console()
new_note.show_to_console()