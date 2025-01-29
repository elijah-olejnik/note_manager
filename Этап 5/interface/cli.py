from curses import wrapper
from datetime import datetime
import colorama
from colorama import Fore, Style
from data import NoteManager, Note
from .femto import femto
from resources import strings
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
        """The function handles 'are you sure? yes/no routines.'"""
        while True:
            user_input = input(strings.confirmation_message_str).strip().lower()
            if user_input in ('yes', 'да'):
                return True
            elif user_input in ('no', 'нет'):
                return False
            else:
                pass

    @staticmethod
    def _print_note_full(note):
        """The function prints out all fields of a given Note object in a user-readable format."""
        row_format = "{:<22} | {:<60}"
        print("-" * 77)
        print(row_format.format(Fore.CYAN + strings.note_id_str + Style.RESET_ALL, str(note.id_)))
        print(row_format.format(Fore.GREEN + strings.username_str + Style.RESET_ALL, note.username))
        print(row_format.format(Fore.YELLOW + strings.title_str + Style.RESET_ALL, note.title))
        print(row_format.format(Fore.MAGENTA + strings.content_str + Style.RESET_ALL, "\n" + note.content))
        print(row_format.format(Fore.BLUE + strings.status_str + Style.RESET_ALL, note.status.name))
        print(row_format.format(Fore.RED + strings.created_date_str + Style.RESET_ALL,
                                date_to_str(note.created_date, False)))
        print(row_format.format(Fore.RED + strings.issue_date_str + Style.RESET_ALL,
                                date_to_str(note.issue_date, True, note.status)))
        print("-" * 77)

    @staticmethod
    def _print_note_short(note, deadline=""):
        """The function prints out created date and title of a given Note object in a user-readable format."""
        print(f"{Fore.CYAN}{date_to_str(note.created_date, False)}"
              f"{Style.RESET_ALL} {note.title} {Fore.RED}{deadline}")

    @staticmethod
    def _get_value_from_console(input_type, prompt="", enum_=None):
        """The function handles and checks the correctness of the user input from terminal
        depending on the given InputType value. The argument 'prompt' is used for the input()
        function, the argument 'enum_' used only if the InputType is InputType.ENUM_VAL.
        Raises a KeyError and ValueError exceptions if input is incorrect.
        """
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
        """The function lists all notes stored by the NoteManager in shortened format."""
        for i, note in enumerate(self._note_manager.notes):
            self._print_note_short(note)

    def _display_notes(self, notes_list, display_full=True, per_page=3):
        """The function displays the given note_list in the user-readable format paged with
        the given parameters: full or shortened and number of notes per page.
        """
        if not notes_list:
            print('\n' + strings.no_notes_disp_str, '\n')
            return
        total_notes = len(notes_list)
        page = 0
        while True:
            start_index = page * per_page
            end_index = start_index + per_page
            notes_to_display = notes_list[start_index:end_index]
            for n in notes_to_display:
                self._print_note_full(n) if display_full else self._print_note_short(n)
            print(strings.page_str, str(page + 1), strings.total_str, str((total_notes + per_page - 1) // per_page))
            print("n -", strings.next_pg_str, "p -", strings.prev_pg_str, "q -", strings.quit_str)
            choice = input(strings.enter_choice_str).lower()
            if choice == 'n':
                if end_index < total_notes:
                    page += 1
                else:
                    print(strings.last_pg_str)
            elif choice == 'p':
                if start_index > 0:
                    page -= 1
                else:
                    print(strings.first_pg_str)
            elif choice == 'q':
                break
            else:
                print(strings.invalid_choice_str, strings.correct_cmds_str, "'n', 'p', or 'q'.")

    def _display_all(self):
        """The function displays all notes stored in NoteManager with
        the parameters given by user input.
        """
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
        """The function handles the note creation from the console."""
        note_args = {
            "username" : strings.enter_username_str,
            "title" : strings.enter_title_str,
            "content" : "",
            "status" : NoteStatus.TERMLESS,
            "issue_date" : strings.enter_issue_str
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
        print('\n' + strings.note_created_str, '\n')
        self._print_note_full(note)

    def _choose_note(self):
        """The function handles the user note choice."""
        notes = []
        while True:
            choice = self._get_value_from_console(
                InputType.STR,
                "\n1." + strings.search_str + "\n2." + strings.show_all_str + "\n\n" +  strings.enter_choice_str
            )
            if choice == '1':
                notes = self._search_notes()
                break
            elif choice == '2':
                notes = self._note_manager.notes
                break
            continue
        if not notes:
            print(f"\n{strings.no_notes_found_str}\n")
            return None
        while True:
            i = self._note_choose_submenu(notes) - 1
            if i not in range(0, len(notes)):
                print(f"\n{strings.invalid_choice_str}\n")
                continue
            try:
                note = self._note_manager.get_note_by_id(notes[i].id_)
                print('\n' + strings.note_chosen_str, "\n\n")
                self._print_note_full(note)
                return note
            except ValueError as e:
                print(e)
                return None

    def _update_note(self):
        """The note handles the note edition in console."""
        note = self._choose_note()
        if not note:
            return
        while True:
            try:
                what_to_edit = self._update_submenu()
                match what_to_edit:
                    case '1':
                        input_value = self._get_value_from_console(InputType.STR, strings.enter_username_str)
                        if not self._user_confirmation():
                            continue
                        note.username = input_value
                    case '2':
                        input_value = self._get_value_from_console(InputType.STR, strings.enter_title_str)
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
                        input_value = self._get_value_from_console(InputType.DATE, strings.enter_issue_str)
                        if not self._user_confirmation():
                            continue
                        note.issue_date = input_value
                    case '6':
                        break
                    case _:
                        continue
                self._note_manager.save_notes_to_file()
                print(strings.note_updated_str, '\n')
                self._print_note_full(note)
            except ValueError as e:
                print('\n', e, '\n')
                continue

    def _delete_note(self):
        """The function handles the note deletion from console."""
        note = self._choose_note()
        try:
            deleted = self._note_manager.delete_note_by_id(note.id_)
            self._note_manager.save_notes_to_file()
            print(strings.note_str, deleted.title, date_to_str(deleted.created_date, False), strings.del_str)
        except ValueError as e:
            print(e)

    def _search_notes(self):
        """The function provide the NoteManager filtering
        options to the user for searching a note from console.
        """
        while True:
            command = self._search_submenu()
            if command == '4':
                break
            keywords = None
            if command in ('2', '3'):
                keywords = [key.strip().lower() for key in
                            input(strings.enter_k_wds_str + "; : ").split(';')]
            state = None
            if command in ('1', '3'):
                state = self._state_submenu()
            notes = self._note_manager.filter_notes(keywords, state)
            if not notes:
                print('\n' + strings.no_matches_fnd_str, '\n')
                continue
            return notes
        return []

    def _note_choose_submenu(self, notes):
        """The submenu routine."""
        print('\n' + strings.choose_note_str, "\n\n")
        for i, note in enumerate(notes):
            print(
                Fore.YELLOW + str(i + 1) + Style.RESET_ALL,
                note.title, Fore.CYAN + date_to_str(note.created_date, False) + Style.RESET_ALL)
        return self._get_value_from_console(InputType.INT, '\n' + strings.enter_choice_str)

    def _state_submenu(self):
        """The submenu routine."""
        print(
            '\n'+ strings.choose_state_str + "\n\n" +
            "0 " + strings.or_str + " active\n"
            "1 " + strings.or_str + " completed\n"
            "2 " + strings.or_str + " postponed\n"
            "3 " + strings.or_str + " termless\n"
        )
        return self._get_value_from_console(InputType.ENUM_VAL, strings.enter_choice_str, NoteStatus)

    def _display_submenu(self):
        """The submenu routine."""
        print(
            f"{Fore.GREEN}\n{strings.note_disp_ops}{Style.RESET_ALL}\n\n"
            f"{strings.show_str} {Fore.MAGENTA}{strings.full_str}{Style.RESET_ALL} | {Fore.CYAN}{strings.short_str}"
            f"{Style.RESET_ALL}: {Fore.MAGENTA}f{Style.RESET_ALL} | {Fore.CYAN}s\n{Style.RESET_ALL}"
            f"{strings.sort_str} {Fore.MAGENTA}{strings.created_date_str.lower()}{Style.RESET_ALL} | {Fore.CYAN}"
            f"{strings.issue_date_str.lower()}{Style.RESET_ALL}: {Fore.MAGENTA}c{Style.RESET_ALL} | {Fore.CYAN}i\n"
            f"{Style.RESET_ALL}"
            f"{Fore.MAGENTA}{strings.asc_str}{Style.RESET_ALL} | {Fore.CYAN}{strings.desc_str}"
            f"{Style.RESET_ALL}: {Fore.MAGENTA}a {Style.RESET_ALL}| {Fore.CYAN}d\n{Style.RESET_ALL}"
        )
        while True:
            param_set = set(
                self._get_value_from_console(InputType.STR, strings.enter_disp_ops_str + " fcd): ").lower()
            )
            if len(param_set) < 3 or not param_set.issubset(set("acdfis")): # noqa
                continue
            else:
                return param_set

    def _update_submenu(self):
        """The submenu routine."""
        print(
            f"{Fore.GREEN}\n{strings.edit_menu_str}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} {strings.username_str}\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} {strings.title_str}\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} {strings.content_str}\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} {strings.status_str}\n"
            f"{Fore.YELLOW}5.{Style.RESET_ALL} {strings.issue_date_str}\n"
            f"{Fore.YELLOW}6.{Style.RESET_ALL} {strings.back_str}\n"
        )
        return self._get_value_from_console(InputType.STR, strings.enter_choice_str)

    def _search_submenu(self):
        """The submenu routine."""
        print(
            f"{Fore.GREEN}\n{strings. search_by_str}:{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} {strings.status_str}\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} {strings.k_wds_str}\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} {strings.both_str}\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} {strings.back_str}\n"
        )
        return self._get_value_from_console(InputType.STR, strings.enter_choice_str)

    def _main_menu(self):
        """The CLI Main menu."""
        if not self._note_manager.notes:
            print(f"\n{Fore.YELLOW}{strings.no_notes_found_str}{Style.RESET_ALL}")
        else:
            self._deadline_check_and_notify()
        print(
            f"{Fore.GREEN}\n{strings.main_menu_str}{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} {strings.create_note_str}\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} {strings.show_all_str}\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} {strings.upd_note_str}\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} {strings.del_note_str}\n"
            f"{Fore.YELLOW}5.{Style.RESET_ALL} {strings.search_str}\n"
            f"{Fore.YELLOW}6.{Style.RESET_ALL} {strings.quit_str.capitalize()}\n"
        )
        return self._get_value_from_console(InputType.STR, strings.enter_choice_str)

    def _set_language(self):
        """Language choice routine."""
        while True:
            choice = self._get_value_from_console(InputType.STR, "Switch language to russian? y | n: ")
            if choice not in ('y', 'n'):
                continue
            if choice == 'y':
                strings.change_language('ru')
            break

    def _deadline_check_and_notify(self):
        """The function checks the notes with urgent deadline
        and notifies the user.
        """
        urgent_notes = self._note_manager.get_urgent_notes_sorted()
        if not urgent_notes:
            return
        if urgent_notes[0]:
            print(f"\n{Fore.RED}{strings.missed_str}", len(urgent_notes[0]), f"\n{Style.RESET_ALL}")
            for note in urgent_notes[0]:
                self._print_note_short(note, date_to_str(note.issue_date, True, note.status))
        if urgent_notes[1]:
            print('\n' + strings.today_str, len(urgent_notes[1]), '\n')
            for note in urgent_notes[1]:
                self._print_note_short(note)
        if urgent_notes[2]:
            print('\n' + strings.tomorrow_str, len(urgent_notes[2]), '\n')
            for note in urgent_notes[2]:
                self._print_note_short(note)

    def run(self):
        """The main function of the CLI."""
        self._set_language()
        print('\n' + strings.welcome_str)
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
