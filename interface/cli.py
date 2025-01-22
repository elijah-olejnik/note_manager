from curses import wrapper
from datetime import datetime
import colorama
from colorama import Fore, Style
from data import NoteManager, Note
from interface.femto import femto
from utils import NoteStatus, InputType, str_to_date, date_to_str, generate_id, input_to_enum_value


class NoteManagerCLI:
    """The class NoteManagerCLI represents an interface to work with
    the NoteManager class (a model Presenter) and handles user interaction
    with the terminal (the View), providing the text-based menus and
    displaying user-readable data.
    """
    def __init__(self):
        self._note_manager = NoteManager()
        colorama.init(autoreset=True)

    @staticmethod
    def _user_confirmation():
        while True:
            user_input = input("Are you sure? yes | no: ")
            if user_input == 'yes':
                return True
            elif user_input == 'no':
                return False
            else:
                pass

    @staticmethod
    def _print_note_full(note):
        row_format = "{:<20} | {:<60}"
        print("-" * 77)
        print(row_format.format(Fore.CYAN + "Note ID" + Style.RESET_ALL, str(note.id_)))
        print(row_format.format(Fore.GREEN + "Username" + Style.RESET_ALL, note.username))
        print(row_format.format(Fore.YELLOW + "Title" + Style.RESET_ALL, note.title))
        print(row_format.format(Fore.MAGENTA + "Content" + Style.RESET_ALL, "\n" + note.content))
        print(row_format.format(Fore.BLUE + "Status" + Style.RESET_ALL, note.status.name))
        print(row_format.format(Fore.RED + "Created" + Style.RESET_ALL, date_to_str(note.created_date, False)))
        print(row_format.format(Fore.RED + "Deadline" + Style.RESET_ALL, date_to_str(note.issue_date, True)))
        print("-" * 77)

    @staticmethod
    def _print_note_short(note, deadline=""):
        print(f"{Fore.CYAN}{date_to_str(note.created_date, False)}{Style.RESET_ALL} {note.title} {Fore.RED}{deadline}\n\n")

    @staticmethod
    def _get_value_from_console(input_type, prompt="", enum_=None):
        while True:
            try:
                user_input = input(prompt).strip() if input_type != InputType.TEXT else wrapper(femto, prompt)
                if not user_input and input_type != InputType.DATE:
                    continue
                match input_type:
                    case InputType.INT:
                        return int(user_input)
                    case InputType.ENUM_VAL:
                        return input_to_enum_value(user_input, enum_)
                    case InputType.DATE:
                        return str_to_date(user_input)
                    case _:
                        return user_input
            except (KeyError, ValueError) as e:
                print('\n', e, '\n')

    def _list_notes(self):
        for i, note in enumerate(self._note_manager.notes):
            self._print_note_short(note)

    def _display_notes(self, notes_list, display_full=True, per_page=3):
        if not notes_list:
            print("\nNo notes to display.\n")
            return
        total_notes = len(notes_list)
        page = 0
        while True:
            start_index = page * per_page
            end_index = start_index + per_page
            notes_to_display = notes_list[start_index:end_index]
            for n in notes_to_display:
                self._print_note_full(n) if display_full else self._print_note_short(n)
            print(f"Page {page + 1} of {(total_notes + per_page - 1) // per_page}")
            print("n - next page, p - previous page, q - quit")
            choice = input("Enter choice: ").lower()
            if choice == 'n':
                if end_index < total_notes:
                    page += 1
                else:
                    print("You are on the last page.")
            elif choice == 'p':
                if start_index > 0:
                    page -= 1
                else:
                    print("You are on the first page.")
            elif choice == 'q':
                break
            else:
                print("Invalid choice. Please enter 'n', 'p', or 'q'.")

    def _display_all(self):
        params = self._display_submenu()
        self._display_notes(
            self._note_manager.sort_notes(
                self._note_manager.notes,
                True if 'c' in params else False,
                True if 'd' in params else False,
            ),
            True if 'f' in params else False
        )

    def _create_note(self):
        note_args = {
            "username" : "Enter a username: ",
            "title" : "Enter a title: ",
            "content" : "",
            "status" : NoteStatus.TERMLESS,
            "issue_date" : "Enter note deadline (dd-mm-yyyy hh:mm): "
        }
        for key, value in note_args.items():
            match key:
                case "content":
                    note_args[key] = self._get_value_from_console(InputType.TEXT)
                case "status":
                    note_args[key] = self._state_submenu()
                case ("issue_date"):
                    if note_args["status"] in (NoteStatus.COMPLETED, NoteStatus.TERMLESS):
                        note_args[key] = datetime.min
                    else:
                        note_args[key] = self._get_value_from_console(InputType.DATE, value)
                case _:
                    note_args[key] = self._get_value_from_console(InputType.STR, value).strip()
        note_args["created_date"] = datetime.now()
        note_args["id_"] = generate_id()
        note = Note(**note_args)
        self._note_manager.append_note(note)
        print('\n', "Note created:", '\n')
        self._print_note_full(note)

    def _choose_note(self):
        notes = []
        while True:
            choice = self._get_value_from_console(InputType.STR, "\n1. Search\n2.Show all\n\nChoose: ")
            if choice == '1':
                notes = self._search_notes()
                break
            elif choice == '2':
                notes = self._note_manager.notes
                break
            continue
        if not notes:
            print("\nNo notes found.\n")
            return None
        while True:
            i = self._note_choose_submenu(notes) - 1
            if i not in range(0, len(notes)):
                print("\nWrong number.\n")
                continue
            try:
                note = self._note_manager.get_note_by_id(notes[i].id_)
                print("\nYou've chosen this note:\n\n")
                self._print_note_full(note)
                return note
            except ValueError as e:
                print(e)
                return None

    def _update_note(self):
        note = self._choose_note()
        if not note:
            return
        while True:
            try:
                what_to_edit = self._update_submenu()
                match what_to_edit:
                    case '1':
                        input_value = self._get_value_from_console(InputType.STR, "Enter new username: ")
                        if not self._user_confirmation():
                            continue
                        note.username = input_value
                    case '2':
                        input_value = self._get_value_from_console(InputType.STR, "Enter new title: ")
                        if not self._user_confirmation():
                            continue
                        note.title = input_value
                    case '3':
                        input_value = self._get_value_from_console(
                            InputType.TEXT,
                            note.content
                        )
                        if not self._user_confirmation():
                            continue
                        note.content = input_value
                    case '4':
                        input_value = self._state_submenu()
                        if not self._user_confirmation():
                            continue
                        note.status = input_value
                    case '5':
                        input_value = self._get_value_from_console(InputType.DATE, "Enter new deadline date (dd-mm-yyyy hh:mm): ")
                        if not self._user_confirmation():
                            continue
                        note.issue_date = input_value
                    case '6':
                        break
                    case _:
                        continue
                self._note_manager.save_notes_to_file()
                print("Note updated:\n")
                self._print_note_full(note)
            except ValueError as e:
                print('\n', e, '\n')
                continue

    def _delete_note(self):
        note = self._choose_note()
        try:
            deleted = self._note_manager.delete_note_by_id(note.id_)
            self._note_manager.save_notes_to_file()
            print(f'\nNote #{deleted.id_} "{deleted.title}" deleted.')
        except ValueError as e:
            print(e)

    def _search_notes(self):
        while True:
            command = self._search_submenu()
            if command == '4':
                break
            keywords = None
            if command in ('2', '3'):
                keywords = [key.strip().lower() for key in
                            input("Enter keywords, separated by ; : ").split(';')]
            state = None
            if command in ('1', '3'):
                state = self._state_submenu()
            notes = self._note_manager.filter_notes(keywords, state)
            if not notes < 1:
                print("\nNo matches found\n")
                continue
            return notes
        return []

    def _note_choose_submenu(self, notes):
        print("\nChoose note\n\n")
        for i, note in enumerate(notes):
            print(Fore.YELLOW + str(i + 1) + Style.RESET_ALL, note.title, Fore.CYAN + date_to_str(note.created_date, False) + Style.RESET_ALL)
        return self._get_value_from_console(InputType.INT, "\nEnter the note number: ")

    def _state_submenu(self):
        print(
            "\nChoose the new note state:\n\n"
            "0 or active\n"
            "1 or completed\n"
            "2 or postponed\n"
            "3 or termless\n"
        )
        return self._get_value_from_console(InputType.ENUM_VAL, "Enter a word or a number: ", NoteStatus)

    def _display_submenu(self):
        print(
            f"{Fore.GREEN}\nNotes display options{Style.RESET_ALL}\n\n"
            f"Show notes in {Fore.MAGENTA}full {Style.RESET_ALL}| {Fore.CYAN}short {Style.RESET_ALL}mode: {Fore.MAGENTA}f {Style.RESET_ALL}| {Fore.CYAN}s\n{Style.RESET_ALL}"
            f"Sort notes by {Fore.MAGENTA}creation {Style.RESET_ALL}| {Fore.CYAN}deadline {Style.RESET_ALL}date: {Fore.MAGENTA}c {Style.RESET_ALL}| {Fore.CYAN}i\n{Style.RESET_ALL}"
            f"{Fore.MAGENTA}Ascending {Style.RESET_ALL}| {Fore.CYAN}descending{Style.RESET_ALL}: {Fore.MAGENTA}a {Style.RESET_ALL}| {Fore.CYAN}d\n{Style.RESET_ALL}"
        )
        while True:
            param_set = set(self._get_value_from_console(InputType.STR,
                "Enter display options, only 3 supported\n"
                "(e.g. for full-creation-ascending enter fcd): "
            ).lower())
            if len(param_set) < 3 or not param_set.issubset(set("acdfis")): # noqa
                continue
            else:
                return param_set

    def _update_submenu(self):
        print(
            f"{Fore.GREEN}\nNote edit menu{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} Username\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} Title\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} Content\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} Status\n"
            f"{Fore.YELLOW}5.{Style.RESET_ALL} Deadline\n"
            f"{Fore.YELLOW}6.{Style.RESET_ALL} Back to the main menu\n"
        )
        return self._get_value_from_console(InputType.STR, "Enter your choice: ")

    def _search_submenu(self):
        print(
            f"{Fore.GREEN}\nSearch by:{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} State\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} Keywords\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} Both\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} Back to the main menu\n"
        )
        return self._get_value_from_console(InputType.STR, "Enter your choice: ")

    def _main_menu(self):
        if not self._note_manager.notes:
            print(f"\n{Fore.YELLOW}No notes yet.{Style.RESET_ALL}")
        else:
            self._deadline_check_and_notify()
        print(
            f"{Fore.GREEN}\nMain menu{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} Create note\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} Show all notes\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} Update note\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} Delete note\n"
            f"{Fore.YELLOW}5.{Style.RESET_ALL} Search notes\n"
            f"{Fore.YELLOW}6.{Style.RESET_ALL} Quit app\n"
        )
        return self._get_value_from_console(InputType.STR, "Enter your choice: ")

    def _deadline_check_and_notify(self):
        urgent_notes = self._note_manager.get_urgent_notes_sorted()
        if not urgent_notes:
            return
        if urgent_notes[0]:
            print(f"\n{Fore.RED}Notes with missed deadline:", len(urgent_notes[0]), f"\n{Style.RESET_ALL}")
            for note in urgent_notes[0]:
                self._print_note_short(note, date_to_str(note.issue_date, True, note.status))
        if urgent_notes[1]:
            print("\nNotes with today deadline:", len(urgent_notes[1]), '\n')
            for note in urgent_notes[1]:
                self._print_note_short(note)
        if urgent_notes[2]:
            print("\nNotes with deadline tomorrow:", len(urgent_notes[2]), '\n')
            for note in urgent_notes[2]:
                self._print_note_short(note)

    def run(self):
        print("\nWelcome to the note manager!")
        while True:
            command = self._main_menu()
            match command:
                case '1':
                    self._create_note()
                case '2':
                    self._display_all()
                case '3':
                    self._update_note()
                case '4':
                    self._delete_note()
                case '5':
                    self._search_notes()
                case '6':
                    break