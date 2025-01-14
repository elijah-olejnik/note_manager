# initializing the variables
username = "Ilia Oleinik" # User Name
title = "My Python questions" # Note title
# Note content
content = ("\n1. How do I check the sizeof(variable)?\n"
           "2. Where and how the memory is allocated for the variables?\n"
           "3. Is there Heap or Stack concepts in Python?\n"
           "4. How can I manage the padding (alignment in the memory) if the variable is lesser than 4 bytes?\n"
           "5. What are the best memory consumption reduce practices in Python?\n"
           "6. What are the prospects for writing high-performance self-learning models for embedded and IoT "
           "using Python?")
status = "Active" # Note state
created_date = "22-12-2024" # Note creation date
issue_date = "30-12-2024" # Note expiration date

# variable values console output
print("\nUser name:", username)
print("\nTitle:", title)
print("\nContent:\n", content, "\n")
print("Status:", status)
print("Created:", created_date)
print("Expire:", issue_date)
