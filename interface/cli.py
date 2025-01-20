from data import NoteManager, Note
from interface.femto import femto
from utils import NoteStatus, InputType, str_to_deadline
from colorama import Fore, Style
from datetime import datetime
from curses import wrapper
import colorama


class NoteManagerCLI:
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
        print(row_format.format(Fore.CYAN + "Note ID" + Style.RESET_ALL, note.id_))
        print(row_format.format(Fore.GREEN + "Username" + Style.RESET_ALL, note.username))
        print(row_format.format(Fore.YELLOW + "Title" + Style.RESET_ALL, note.title))
        print(row_format.format(Fore.MAGENTA + "Content" + Style.RESET_ALL, "\n" + note.content))
        print(row_format.format(Fore.BLUE + "Status" + Style.RESET_ALL, note.status.name))
        date_display_fmt = "%B %d, %Y %H:%M"
        created = datetime.strftime(note.created_date, date_display_fmt)
        print(row_format.format(Fore.RED + "Created" + Style.RESET_ALL, created))
        if note.status not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
            deadline = datetime.strftime(note.issue_date, date_display_fmt)
        else:
            deadline = "NO DEADLINE"
        print(row_format.format(Fore.RED + "Deadline" + Style.RESET_ALL, deadline))
        print("-" * 77)

    @staticmethod
    def _print_note_short(note):
        print(f"{Fore.CYAN}Note ID #{Style.RESET_ALL}{note.id_}: {note.title}\n\n")

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
                        if not user_input.isdigit():
                            name = user_input.upper()
                            return enum_[name]
                        else:
                            value = int(user_input)
                            return enum_(value)
                    case InputType.DATE:
                        return str_to_deadline(user_input)
                    case _:
                        return user_input
            except (KeyError, ValueError) as e:
                print('\n', e, '\n')

    @classmethod
    def _display_notes(cls, notes_list, display_full=True, per_page=3):
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
                cls._print_note_full(n) if display_full else cls._print_note_short(n)
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
        note = Note(**note_args)
        self._note_manager.append_note(note)
        print('\n', "Note created:", '\n')
        self._print_note_full(note)

    def _update_note(self):
        note_id = self._get_value_from_console(InputType.INT, "\nEnter the note ID to edit: ")
        i = self._note_manager.get_note_index_by_id(note_id)
        if i == -1:
            print(f"\nNote with ID#{note_id} not found.\n")
            return
        while True:
            try:
                what_to_edit = self._update_submenu()
                match what_to_edit:
                    case '1':
                        input_value = self._get_value_from_console(InputType.STR, "Enter new username: ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.notes[i].username = input_value
                    case '2':
                        input_value = self._get_value_from_console(InputType.STR, "Enter new title: ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.notes[i].title = input_value
                    case '3':
                        input_value = self._get_value_from_console(
                            InputType.TEXT,
                            self._note_manager.notes[i].content
                        )
                        if not self._user_confirmation():
                            continue
                        self._note_manager.notes[i].content = input_value
                    case '4':
                        input_value = self._state_submenu()
                        if not self._user_confirmation():
                            continue
                        self._note_manager.notes[i].status = input_value
                    case '5':
                        input_value = self._get_value_from_console(InputType.DATE, "Enter new deadline date (dd-mm-yyyy hh:mm): ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.notes[i].issue_date = input_value
                    case '6':
                        break
                    case _:
                        continue
                self._save_notes()
                print("Note updated:\n")
                self._print_note_full(self._note_manager.notes[i])
            except ValueError as e:
                print('\n', e, '\n')
                continue

    def _save_notes(self):
        if not self._note_manager.export_yaml(self._note_manager.notes, self._archive_path):
            print("\nExport to file failed.\n")

    def _save_note(self, note):
        if not self._note_manager.export_yaml([note], self._archive_path, rewrite=False):
            print("\nFailed to save note.\n")

    def _delete_note(self):
        note_id = self._get_value_from_console(InputType.INT, "Enter the note ID to delete: ")
        i = self._note_manager.get_note_idx_by_id(note_id)
        if i == -1:
            print(f"\nNote with ID#{note_id} not found.\n")
            return
        if not self._user_confirmation():
            return
        deleted = self._note_manager.notes.pop(i)
        self._save_notes()
        print(f'\nNote #{deleted.id_} "{deleted.title}" deleted.')

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
                print("HERE")
                state = self._state_submenu()
            notes = self._note_manager.filter_notes(keywords, state)
            if len(notes) < 1:
                print("\nNo matches found\n")
                continue
            self._display_notes(notes)

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
            if len(param_set) < 3 or not param_set.issubset(set("acdfis")):
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
        if urgent_notes[0]:
            print('\n', "Notes with missed deadline:", len(urgent_notes[0]), '\n')
            for note in urgent_notes[0]:
                print(f"ID #{note.id_}", note.title)
        if urgent_notes[1]:
            print('\n', "Notes with today deadline:", len(urgent_notes[1]), '\n')
            for note in urgent_notes[1]:
                print(f"ID #{note.id_}", note.title)
        if urgent_notes[2]:
            print('\n', "Notes with deadline tomorrow:", len(urgent_notes[2]), '\n')
            for note in urgent_notes[2]:
                print(f"ID #{note.id_}", note.title)

    def run(self):
        print('\n', "Welcome to the note manager!")
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