import sys
from database import*
from utils import DatabaseError, InputType, get_value_from_console

main_menu = """
Main menu

[1] Add note
[2] Load all
[3] Update
[4] Delete
[5] Search
[6] Filter
[7] Quit
"""

status_menu = """
Choose status

[1] ACTIVE
[2] COMPLETED
[3] POSTPONED
[4] TERMLESS
"""

update_menu = """
Update menu

[1] Title
[2] Content
[3] Status
[4] Deadline
[5] Back
"""


def user_confirmation():
    """The function handles 'are you sure? yes/no routines.'"""
    while True:
        user_input = input("Are you sure? [Y] | [N]").strip().lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            pass


def create_note():
    note = {
        "username" : "Enter a username: ",
        "title" : "Enter a title: ",
        "content" : "",
        "status" : "Enter the note state",
        "issue_date" : "Enter note deadline (dd-mm-yyyy hh:mm): "
    }
    for key, value in note.items():
        match key:
            case "content":
                note[key] = get_value_from_console(InputType.TEXT)
            case "status":
                note[key] = menu(status_menu, True)
            case ("issue_date"):
                if note["status"] in (NoteStatus.COMPLETED, NoteStatus.TERMLESS):
                    note[key] = datetime.min
                else:
                    note[key] = get_value_from_console(InputType.DATE, value)
            case _:
                note[key] = get_value_from_console(InputType.STR, value).strip()
    note["created_date"] = datetime.now()
    return note


def update_note(note):
    """The note handles the note edition in console."""
    del note['id'], note['username'], note['created_date']
    while True:
        try:
            what_to_edit = menu(update_menu)
            match what_to_edit:
                case '1':
                    input_value = get_value_from_console(InputType.STR, "Enter new title: ")
                    if not user_confirmation():
                        continue
                    note['title'] = input_value
                case '2':
                    input_value = get_value_from_console(InputType.TEXT, note['content'])
                    if not user_confirmation():
                        continue
                    note['content'] = input_value
                case '3':
                    input_value = menu(status_menu, True)
                    if not user_confirmation():
                        continue
                    note['status'] = input_value
                case '4':
                    input_value = get_value_from_console(
                        InputType.DATE,
                        "Enter new deadline (dd-mm-yyyy): "
                    )
                    if not user_confirmation():
                        continue
                    note.issue_date = input_value
                case '5':
                    return note
                case _:
                    continue
        except ValueError as e:
            print('\n', e, '\n')
            continue


def menu(items: str, is_status=False):
    print(items)
    return input("Enter your choice: ") if not is_status else (
        get_value_from_console(InputType.ENUM_VAL, "Enter status: ", NoteStatus)
    )


def main():
    db_path = "database/notes.db"
    print("\nWelcome to the Note Manager\n")
    try:
        setup_db(db_path)
        while True:
            match(menu(main_menu)):
                case '1':
                    save_note_to_db(create_note(), db_path)
                    print("\nNote added\n")
                case '2':
                    print("\nCurrent notes:\n")
                    print(load_notes_from_db(db_path))
                case '3':
                    notes = load_notes_from_db(db_path)
                    if not notes:
                        continue
                    print("\nCurrent notes:\n")
                    print(notes)
                    while True:
                        note_id = get_value_from_console(InputType.INT, "Enter note ID to update: ")
                        note = get_note_by_id(note_id, db_path)
                        if note:
                            break
                    update_note_in_db(note_id, update_note(note), db_path)
                    print("\nNote updated\n")
                case '4':
                    print("\nCurrent notes:\n")
                    print(load_notes_from_db(db_path))
                    note_id = get_value_from_console(InputType.INT, "Enter note ID to delete: ")
                    delete_note_from_db(note_id, db_path)
                    print("\nNote deleted\n")
                case '5':
                    keyword = get_value_from_console(InputType.STR, "Enter a keyword: ")
                    print("\nNotes found:\n")
                    print(search_notes_by_keyword(keyword, db_path))
                case '6':
                    status = menu(status_menu, True)
                    print('\n', status.name, "notes:\n")
                    print(filter_notes_by_status(status, db_path))
                case '7':
                    sys.exit(0)
    except DatabaseError as e:
        print(e)
        sys.exit(-1)


if __name__ == '__main__':
    main()