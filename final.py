from datetime import datetime
from enum import Enum

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
#TODO: refactor the code to merge with add_list.py changes
class Note:
    in_date_fmt = "%d-%m-%Y"
    out_date_fmt = "%A %d %B"

    def __init__(self):
        self.note = {
            "username" : "",
            "titles" : [],
            "content" : "",
            "status" : Status.ACTIVE,
            "created_date" : datetime.today(),
            "issue_date" : "Termless"
        }

    def get_note(self):
        return self.note

    def set_note(self, note=None):
        if note is None:
            note = {}
        self.note = note

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
                        # change to fill the dictionary
                        self.note["status"] = Status.ACTIVE if user_input == 'a' else Status.COMPLETED
                        break
                    if not user_input:
                        if i == 6:
                            self.note["created_date"] = datetime.now()
                        break
                    try:
                        date = datetime.strptime(user_input, self.in_date_fmt)
                        if i == 6:
                            if date.date() != datetime.today().date():
                                print ("\nWhat are you hiding, cheater? =)")
                            self.note["created_date"] = date
                            break
                        if i == 7:
                            if date < self.note["created_date"]:
                                raise ValueError("The expiration date of a note can't be "
                                                 "earlier than the date it was created")
                            self.note["issue_date"] = date
                            break
                    except ValueError as e:
                        print(f"\n{e}")
                        continue
                input_list.append(user_input)
                break
        self.note["username"] = input_list[0]
        self.note["titles"] = input_list[1:4]
        self.note["content"] = input_list[4]

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        return (f"User name: {self.note["username"]}\n"
                f"{"\n".join("Title " + str(i + 1) + ": " + str(t) for i, t in enumerate(self.note["titles"]))}\n"
                f"Content:\n\n{self.note["content"]}\n\n"
                f"Status: {self.note["status"].name}\n"
                f"Created: {datetime.strftime(self.note["created_date"], self.out_date_fmt)}\n"
                f"Expired: {
                datetime.strftime(self.note["issue_date"], self.out_date_fmt)
                if isinstance(self.note["issue_date"], datetime)
                else self.note["issue_date"]
                }\n")

new_note = Note()
new_note.fill_from_console()
new_note.show_to_console()