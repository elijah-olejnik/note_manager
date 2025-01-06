# TODO: Refactor this code from previous tasks to match the new task

def create_note():
    prompts = (
        'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                           'titles/headers within your text,\nuse double curly braces, e.g. {{Some title}}.'
                           '\nUse Enter key to add a new line,\nor type "end" to finish the note input\n',
        'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED, "p" if POSTPONED '
        'or skip pressing Enter if TERMLESS',
        f'Enter the date and time of note creation or press Enter for auto input\nAcceptable formats:\n'
        f'{"\n".join(self._in_date_fmts)}\n\nCreated',
        'Enter the date and time of the deadline or press Enter if termless\nAcceptable formats:\n'
        f'{"\n".join(self._in_date_fmts)}\n\nDeadline'
    )
    note = {}
    for i, prompt in enumerate(prompts):
        while True:
            user_input = input("\n"
                               + prompt
                               + (f" (today is {datetime.strftime(note.created_date, self._in_date_fmts[0])}): "
                                  if i == 3 else ": ")) if i != 1 else curses.wrapper(femto.femto)
            if i < 2 and not user_input:
                continue
            match i:
                case 0:
                    note.username = user_input
                case 1:
                    note.content = user_input
                    note.titles = _extract_titles(user_input)
                case 2:
                    match user_input:
                        case 'a':
                            note.status = Status.ACTIVE
                        case 'c':
                            note.status = Status.COMPLETED
                        case 'p':
                            note.status = Status.POSTPONED
                        case _:
                            note.status = Status.TERMLESS
                case _:
                    if not user_input:
                        break
                    result = self._is_date_acceptable(user_input, i == 4)
                    if result[0]:
                        if i == 3:
                            note.created_date = result[1]
                        elif i == 4:
                            if result[1] < note.created_date:
                                print("\nThe deadline date of a note can't be "
                                      "earlier than the date it was created!")
                                continue
                            note.issue_date = result[1]
                    else:
                        print("\n", result[1])
                        continue
            break
    self._notes.append(note)
    self._save_to_json()
    print("\nYour note is successfully saved\n")