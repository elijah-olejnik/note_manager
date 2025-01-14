import curses
import dataclasses
import sys
import yaml
import colorama
from colorama import Style, Fore
from random import randint
from datetime import datetime
from enum import Enum
from pathlib import Path
from femto import femto  # My tiny console editor


datetime_fmt = "%d-%m-%Y %H:%M"


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


@dataclasses.dataclass
class Note:
    id_: int = randint(10000, 99999)
    username: str = ""
    title: str = ""
    content: str = ""
    status: NoteStatus = NoteStatus.TERMLESS
    created_date: datetime.date = datetime.now()
    issue_date: datetime.date = datetime.min


class NoteManager:
    def __init__(self, notes):
        yaml.add_representer(datetime, self.datetime_representer)
        yaml.add_representer(NoteStatus, self.enum_representer)
        if not notes:
            self._notes = []
        else:
            self._notes = notes

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def str_to_deadline(str_date):
        date = datetime.strptime(str_date, datetime_fmt)
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date

    @staticmethod
    def sort_notes(notes, by_created=True, descending=True):
        if not notes:
            return []
        return sorted(notes, key=lambda x: x.created_date, reverse=descending) if by_created else \
            sorted(notes, key=lambda x: (x.issue_date == datetime.min, x.issue_date), reverse=True)

    @staticmethod
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())

    @staticmethod
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)

    @staticmethod
    def import_yaml(filename):
        try:
            with open(filename, 'r') as file:
                import_list = yaml.safe_load(file)
            return [
                Note(
                    id_=d["id"],
                    username=d["username"],
                    title=d["title"],
                    content=d["content"],
                    status=NoteStatus[d["status"]],
                    created_date=datetime.fromisoformat(d["created_date"]),
                    issue_date=datetime.fromisoformat(d["issue_date"])
                ) for d in import_list
            ]
        except (OSError, ValueError) as e:
            return []

    @staticmethod
    def export_yaml(notes, filename):
        if len(notes) < 1:
            return False
        export_list = [dataclasses.asdict(note) for note in notes]
        try:
            with open(filename, 'w') as file:
                yaml.dump(export_list, file)
            return True
        except (OSError, ValueError):
            return False

    @property
    def notes(self):
        return self._notes

    def _get_note_idx_by_id(self, id_):
        idx = -1
        for i, note in enumerate(self._notes):
            if note.id_ == id_:
                idx = i
        if idx == -1:
            raise ValueError(f"Note with ID #{id_} not found.")
        return idx

    def _get_notes_idx_by_filter(self, keys=None, state=None):
        if not self._notes:
            return []
        filtered_indexes = set()
        for i, note in enumerate(self._notes):
            status_match = (state is None or note.status == state)
            keyword_match = False
            if keys:
                for key in keys:
                    key = key.strip().lower()
                    if (key in note.username.lower()) or \
                            (key in note.title.lower()) or \
                            (key in note.content.lower()):
                        keyword_match = True
                        break
            else:
                keyword_match = True
            if status_match and keyword_match:
                filtered_indexes.add(i)
        return filtered_indexes

    def notes_count(self):
        return len(self._notes)

    def add_note(self, note):
        self._notes.append(note)

    def get_note_by_id(self, id_):
        return self._notes[self._get_note_idx_by_id(id_)]

    def filter_notes(self, keys=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(keys, state)
        return [self._notes[i] for i in found_indexes] if found_indexes else []

    def pop_note(self, id_):
        i = self._get_note_idx_by_id(id_)
        note = self._notes.pop(i)
        return note

    def delete_filtered(self, name=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(name, state)
        if not found_indexes:
            raise KeyError("Can't delete non-existing notes")
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]

    def clear(self):
        if len(self._notes) > 0:
            self._notes.clear()

    # Notes deadline check
    def get_urgent_notes_sorted(self):
        missed_dl = []
        today_dl = []
        oneday_dl = []
        for note in self._notes:
            if note.status not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
                days = (note.issue_date - datetime.now()).days
                if days < 0:
                    missed_dl.append((note, days))
                elif days == 0:
                    today_dl.append(note)
                elif days == 1:
                    oneday_dl.append(note)
        return [self.sort_notes(missed_dl, False, False), today_dl, oneday_dl]


class InputType(Enum):
    INT = 0
    STR = 1
    TEXT = 2
    ENUM_VAL = 3
    DATE = 4


# NoteManager CLI and a set of terminal utility functions
class NoteManagerCLI:
    def __init__(self, archive=""):
        self._archive_path = archive
        self._note_manager = NoteManager(NoteManager.import_yaml(self._archive_path)) \
            if self._archive_check(archive) else NoteManager([])

    @staticmethod
    def _archive_check(pathname):
        archive = Path(pathname)
        if archive.is_file() and archive.stat().st_size > 0:
            return True
        return False

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
        print(row_format.format(Fore.MAGENTA + "Content" + Style.RESET_ALL, note.content))
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
                user_input = input(prompt) if input_type != InputType.TEXT else curses.wrapper(femto, prompt)
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
                        return NoteManager.str_to_deadline(user_input)
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
        note_args = [
            "Enter a username: ",
            "Enter a title: ",
            "", "Enter note state: ",
            "Enter note deadline: "
        ]
        for i, arg in enumerate(note_args):
            match i:
                case 2:
                    note_args[i] = self._get_value_from_console(InputType.TEXT)
                case 3:
                    note_args[i] = self._state_submenu()
                case 4:
                    if note_args[3] in (NoteStatus.COMPLETED, NoteStatus.TERMLESS):
                        note_args[i] = datetime.min
                    else:
                        note_args[i] = self._get_value_from_console(InputType.DATE, arg)
                case _:
                    note_args[i] = self._get_value_from_console(InputType.STR, arg)
        note = Note(*note_args)
        self._note_manager.add_note(note)
        self._save_notes()
        print('\n', "Note created:", '\n')
        self._print_note_full(note)

    def _update_note(self):
        while True:
            try:
                what_to_edit = self._update_submenu()
                match what_to_edit[0]:
                    case 1:
                        input_value = self._get_value_from_console(InputType.STR, "Enter new username: ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.get_note_by_id(what_to_edit[1]).username = input_value
                    case 2:
                        input_value = self._get_value_from_console(InputType.STR, "Enter new title: ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.get_note_by_id(what_to_edit[1]).title = input_value
                    case 3:
                        input_value = self._get_value_from_console(
                            InputType.TEXT,
                            self._note_manager.get_note_by_id(what_to_edit[1]).content
                        )
                        if not self._user_confirmation():
                            continue
                        self._note_manager.get_note_by_id(what_to_edit[1]).content = input_value
                    case 4:
                        input_value = self._state_submenu()
                        if not self._user_confirmation():
                            continue
                        self._note_manager.get_note_by_id(what_to_edit[1]).status = input_value
                    case 5:
                        input_value = self._get_value_from_console(InputType.DATE, "Enter new deadline date: ")
                        if not self._user_confirmation():
                            continue
                        self._note_manager.get_note_by_id(what_to_edit[1]).issue_date = input_value
                    case 6:
                        break
                    case _:
                        continue
                self._save_notes()
                print("Note updated:\n")
                self._print_note_full(self._note_manager.get_note_by_id(what_to_edit[1]))
            except ValueError as e:
                print('\n', e, '\n')
                continue

    def _save_notes(self):
        if not self._note_manager.export_yaml(self._note_manager.notes, self._archive_path):
            print("\nExport to file failed.\n")

    def _delete_note(self):
        note_id = self._get_value_from_console(InputType.INT, "Enter the note ID to delete: ")
        if not self._user_confirmation():
            return
        deleted = self._note_manager.pop_note(note_id)
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
            "Notes display options\n\n"
            "Show notes in full | short mode: f | s\n"
            "Sort notes by creation | deadline date: c | i\n"
            "Ascending | descending: a | d\n"
        )
        while True:
            param_set = set(self._get_value_from_console(InputType.STR,
                "Enter display options, only 3 supported\n"
                "(e.g. for full-creation-ascending enter fcd):"
            ))
            if len(param_set) < 3 or not param_set.issubset(set("acdfis")):
                continue
            else:
                return param_set

    def _update_submenu(self):
        note_id = self._get_value_from_console(InputType.INT, "Enter the note ID to edit: ")
        print(
            "\nNote edit menu\n\n"
            "1. Username\n"
            "2. Title\n"
            "3. Content\n"
            "4. Status\n"
            "5. Deadline\n"
            "6. Back to the main menu\n"
        )
        choice = self._get_value_from_console(InputType.STR, "Enter your choice: ")
        return choice, note_id

    def _search_submenu(self):
        print(
            "\nSearch by:\n\n"
            "1 - state\n"
            "2 - keywords\n"
            "3 - both\n"
            "4 - Back to the main menu\n"
        )
        return self._get_value_from_console(InputType.STR, "Enter your choice: ")

    def _main_menu(self):
        print(
            f"{Fore.GREEN}\nMain menu{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}1.{Style.RESET_ALL} Create note\n"
            f"{Fore.YELLOW}2.{Style.RESET_ALL} Show all notes\n"
            f"{Fore.YELLOW}3.{Style.RESET_ALL} Update note\n"
            f"{Fore.YELLOW}4.{Style.RESET_ALL} Delete note\n"
            f"{Fore.YELLOW}5.{Style.RESET_ALL} Search notes\n"
            f"{Fore.YELLOW}6.{Style.RESET_ALL}2 Quit app\n"
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
        self._deadline_check_and_notify()
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


def main():
    if sys.stdout.isatty():
        colorama.init(autoreset=True)
        term = NoteManagerCLI("notes.yaml")
        term.run()
    # Here is the place for GUI initialization
    return 0


if __name__ == "__main__":
    main()