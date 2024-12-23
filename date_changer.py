import time as t # This library is needed mostly for user input control, but we can us it for the date storing
from time import strftime

date_fmt = "%d-%m-%Y" # We restrict the date input to this format

# We need to check the user input, but we don't want to write similar code for every data field so we need a loop and
# the following sequence of messages as a list for a user input loop
prompt_list = ['Enter your name', 'Enter the note title', 'Enter the note text', 'Enter the note state',
               'Enter the date of note creation in "dd-mm-yyyy" format',
               'Enter the note expiration date in "dd-mm-yyyy" format']
input_list = [] # A temporary list for user input data storing (we're lucky it's always strings)
temp_str = None # A temporary variable to store the user input

# Here goes the user input loop in which we define our 6 variables
for i in range(6):
    # An eternal loop for the input mistakes handling inside
    while True:
        temp_str = input(f"\n" + prompt_list[i] + ": ") # Getting the user input
        # Try-except block is added mostly for the ValueError exceptions caught from the time.strptime() function, but
        # also we can use it for the null input control
        try:
            # null-check condition
            if temp_str:
                # Here we need to separate 2 last iterations to check the date input correctness and if the date format
                # is wrong, we should catch the ValueError exception, after converting the function result to a bool
                if i > 3 and bool(t.strptime(temp_str, date_fmt)):
                    input_list.append(temp_str)
                    break
                input_list.append(temp_str) # If null-check passed the first 4 iterations will add user input
                # to the list
                break # and exit from the while loop
            else:
                raise ValueError # Here we throw an exception (since we already have try-catch block) if string is null
        except ValueError:
            # When the exception is caught, we notify the user and return to the beginning of the while loop
            print("\nYour input is incorrect, try again")

del prompt_list, temp_str # Not needed anymore

# initializing the variables with user input
username = input_list[0]  # User Name
title = input_list[1] # Note title
content = input_list[2] # Note content
status = input_list[3] # Note state
created_date = t.strptime(input_list[4], date_fmt) # Note creation date converted to time variable
issue_date = t.strptime(input_list[5], date_fmt) # Note expiration date converted to time variable

del input_list, date_fmt # Not needed anymore

# Show saved fields to the console output
print("\nYour note is saved. You've entered: ")
print("\nUser name:", username)
print("\nTitle:", title)
print("\nContent:\n", content, "\n")
print("Status:", status)
print("Created:", strftime("%a, %d %b", created_date)) # Converting without a year from time variable
print("Expired:", strftime("%a, %d %b", issue_date)) # Converting without a year from time variable