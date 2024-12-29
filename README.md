# note_manager
## Grade 1
### Stage 1
#### greetings.py
    This script prints out to console 6 the values of predefined 
    variables of the Note sketch with some formatting:

    1. User Name
    2. Title
    3. Content (The note text block)
    4. Status (Active, Completed)
    5. Date of creation
    6. Issue date
#### date_changer.py
    This script asks user to input the values for the note 
    (as it was indicated in the example attached to the task),
    saves the values to the class attributes and then prints 
    them out formatted to the console, dates are printed without year.

    So, this piece of code contain:

    1. datetime library for simple date conversions and comparison
    2. class Note
    3. console user input function with error handling logic
#### add_input.py
    This script adds some performance and code optimisations and 
    the list for saving 3 titles (as it was indicated in the example 
    attached to the task)
#### add_list.py
    I thought that it will be more convenient to add titles 
    (as many as you want) right in your note text while typing
    it into console, something like this:
    ~~Title 1~~ text ~~Title 2~~ text, etc..
    So I added that feature and also made my code 
    more readable with several optimisations: 

    1. I added the match-case statement in the fill_from_console() 
    function instead of complicated if-else conditions
    2. Separated the date input checkings to the private 
    function _is_date_accepted()
    3. Added an additional note status: TERMLESS
#### final_list.py & final_dict.py
    These scripts still doing much the same but (as a new feature) 
    one saves the values to the list and another one - to the dictionary.
    Both options were in the tasks so I made both. Also I used
    regular expressions for title detection so user will type
    headers in more convenient way: {{Title}} text {{Title 2}} text, etc.
### Stage 2
#### add_titles_loop.py
    This script asks user to add titles and saves them to the list if inputted
    string is unique and not empty. The stop word is "quit" so if the program
    get this word as the user input it prints all titles back to console and quit. 