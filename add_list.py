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
        self.titles = ["", "", ""] # TODO: I need to refactor my code for multiple title input
        self.content = None
        self.status = None
        self.created_date = None
        self.issue_date = "Termless"

    def fill_from_console(self):
        prompt_list = ('Enter your name', 'Enter a title',
                       'Enter a second title or press Enter to skip',
                       'Enter a third title or press Enter to skip',
                       'Enter the note text', 'Enter the note state: "a" if Active or "c" if Completed',
                       'Enter the date of note creation in "dd-mm-yyyy" format or press Enter for auto input',
                       'Enter the note expiration date in "dd-mm-yyyy" format or press Enter if termless')
        input_list = []
        for i, prompt in enumerate(prompt_list):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(datetime.today(), self.in_date_fmt)}): "
                                   if i == 6 else ": "))
                if (i not in (2, 3, 6, 7) and not user_input) or (i == 5 and user_input not in ('c', 'a')):
                    continue
                if i > 4:
                    if i == 5:
                        self.status = Status.ACTIVE if user_input == 'a' else Status.COMPLETED
                        break
                    if not user_input:
                        if i == 6:
                            self.created_date = datetime.now()
                        break
                    try:
                        date = datetime.strptime(user_input, self.in_date_fmt)
                        if i == 6:
                            if date.date() != datetime.today().date():
                                print ("\nWhat are you hiding, cheater? =)")
                            self.created_date = date
                            break
                        if i == 7:
                            if date < self.created_date:
                                raise ValueError("The expiration date of a note can't be "
                                                 "earlier than the date it was created")
                            self.issue_date = date
                            break
                    except ValueError as e:
                        print(f"\n{e}")
                        continue
                input_list.append(user_input)
                break
        self.username = input_list[0]
        for i in range(3):
            self.titles[i] = input_list[i + 1]
        self.content = input_list[4]

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