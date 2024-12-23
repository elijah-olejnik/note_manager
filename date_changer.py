from datetime import datetime

class Note:
    in_date_fmt = "%d-%m-%Y"
    out_date_fmt = "%A %d %B"

    def __init__(self):
        self.username = None
        self.title = None
        self.content = None
        self.status = None
        self.created_date = None
        self.issue_date = None
        self.tmp_date = None

    def handle_user_input(self, prompt, is_date=False, is_issue_date=False):
        while True:
            user_input = input("\n" + prompt + ": ")
            try:
                if user_input:
                    if is_date:
                        date = datetime.strptime(user_input, self.in_date_fmt)
                        if is_issue_date:
                            if date < self.tmp_date:
                                raise ValueError("The expiration date can't be earlier than the creation date!")
                        self.tmp_date = date
                        return date
                    return user_input
                else:
                    raise ValueError("You've entered nothing")
            except ValueError as e:
                print("\nThe input is incorrect: ", e)

    def fill_with_console(self):
        prompt_list = ['Enter your name', 'Enter the note title', 'Enter the note text', 'Enter the note state',
                       'Enter the date of note creation in "dd-mm-yyyy" format',
                       'Enter the note expiration date in "dd-mm-yyyy" format']
        input_list = [self.handle_user_input(prompt, i > 3, i > 4) for i, prompt in enumerate(prompt_list)]
        self.username, self.title, self.content, self.status, self.created_date, self.issue_date = input_list

    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    def __str__(self):
        return (f"User name: {self.username}\n"
                f"Title: {self.title}\n"
                f"Content:\n\n{self.content}\n\n"
                f"Status: {self.status}\n"
                f"Created: {datetime.strftime(self.created_date, self.out_date_fmt)}\n"
                f"Expired: {datetime.strftime(self.issue_date, self.out_date_fmt)}\n")

new_note = Note()
new_note.fill_with_console()
new_note.show_to_console()