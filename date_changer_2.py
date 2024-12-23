from datetime import datetime # This library is needed for date handling

# Since a note is an object we can store in a database let's make a class for it
class Note:
    in_date_fmt = "%d-%m-%Y"  # We restrict the date input to this format
    out_date_fmt = "%A %d %B" # We restrict the date output to this format

    # Initialisation of the class fields
    def __init__(self):
        self.username = None # User Name
        self.title = None # Note title
        self.content = None # Note content
        self.status = None # Note state
        self.created_date = None # Note creation date
        self.issue_date = None # Note expiration date
        self.tmp_date = None # Needed for date input check

    # This function is needed to handle user input mistakes: we don't need empty fields, or incorrect dates
    def handle_user_input(self, prompt, is_date=False, is_issue_date=False):
        # The infinite loop for user input attempts
        while True:
            user_input = input("\n" + prompt + ": ") # Getting user input
            # the following try-catch block is added mostly for the ValueError exceptions caught from the
            # datetime.strptime() function, but also we can use it for the null input control
            try:
                # Non-null check
                if user_input:
                    # Checking if we reached date block input
                    if is_date:
                        # Conversion to the datetime object can raise the ValueError so we're ready for it
                        date = datetime.strptime(user_input, self.in_date_fmt)
                        # Checking if we reached the last iteration
                        if is_issue_date:
                            # Checking if the issue date is bigger than creation date
                            if date < self.tmp_date:
                                raise ValueError("The expiration date can't be earlier than the creation date!")
                        self.tmp_date = date # Here we need to save the value from the 5th iteration for comparison
                        return date # Date return statement
                    return user_input # Default user input return statement
                else:
                    raise ValueError("You've entered nothing") # If input is null we move to the exception block
            except ValueError as e:
                print("\nThe input is incorrect: ", e) # We always should notify the User about his faults

    # This function is needed to fill our class with data from console input
    def fill_with_console(self):
        # Here's the sequence of messages as a list for a user input loop
        prompt_list = ['Enter your name', 'Enter the note title', 'Enter the note text', 'Enter the note state',
                       'Enter the date of note creation in "dd-mm-yyyy" format',
                       'Enter the note expiration date in "dd-mm-yyyy" format']
        # This for-loop fills the temporary list from which the class fields are defined
        input_list = [self.handle_user_input(prompt, i > 3, i > 4) for i, prompt in enumerate(prompt_list)]
        self.username, self.title, self.content, self.status, self.created_date, self.issue_date = input_list

    # Show Note info via console
    def show_to_console(self):
        print("\nYour note is saved. You've entered:\n")
        print(self.__str__())

    # This method is for getting the Note info
    def __str__(self):
        return (f"User name: {self.username}\n"
                f"Title: {self.title}\n"
                f"Content:\n\n{self.content}\n\n"
                f"Status: {self.status}\n"
                f"Created: {datetime.strftime(self.created_date, self.out_date_fmt)}\n"
                f"Expired: {datetime.strftime(self.issue_date, self.out_date_fmt)}\n")

new_note = Note() # Finally, we create our note object here
new_note.fill_with_console() # Getting the user input
new_note.show_to_console() # Showing what we have saved