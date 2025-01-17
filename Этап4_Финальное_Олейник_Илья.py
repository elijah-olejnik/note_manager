import curses
import dataclasses
import sys
import threading
import warnings
import pygame
import yaml
import colorama
from colorama import Style, Fore
from random import randint
from datetime import datetime
from enum import Enum
from pathlib import Path
from femto import femto

datetime_fmt = "%d-%m-%Y %H:%M"


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


class DataIntegrityError(Exception):
    pass


@dataclasses.dataclass
class Note:
    content: str
    issue_date: datetime.date
    status: NoteStatus
    title: str
    username: str
    created_date: datetime.date = datetime.now()
    id_: int = randint(10000, 99999)


class NoteManager:
    def __init__(self, notes):
        yaml.add_representer(datetime, self.datetime_representer)
        yaml.add_representer(NoteStatus, self.enum_representer)
        self._notes = notes if notes else []

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def str_to_deadline(str_date):
        try:
            date = datetime.strptime(str_date, datetime_fmt)
            if date <= (datetime.now()):
                raise ValueError("The deadline can be only in the future.")
            return date
        except ValueError as e:
            raise e

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
        required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
        try:
            with open(filename, 'r') as file:
                import_list = yaml.safe_load(file)
            if not import_list:
                raise ValueError(f"File {filename} is empty!")
            notes_list = []
            for d in import_list:
                if not all(field in d for field in required_fields):
                    raise DataIntegrityError(f"Missing required fields in record: {d}")
                try:
                    note = Note(
                        content=d["content"],
                        created_date=datetime.fromisoformat(d["created_date"]),
                        id_=d["id_"],
                        issue_date=datetime.fromisoformat(d["issue_date"]),
                        status=NoteStatus[d["status"]],
                        title=d["title"],
                        username=d["username"]
                    )
                    notes_list.append(note)
                except(ValueError, KeyError, TypeError) as e:
                    raise DataIntegrityError(f"Data format error in record {d}: {e}.")
            return notes_list
        except (OSError, ValueError, yaml.YAMLError, DataIntegrityError) as e:
            warnings.warn(e)
            return []

    @staticmethod
    def export_yaml(notes, filename, rewrite = True):
        if not notes:
            return False
        export_list = [dataclasses.asdict(note) for note in notes]
        try:
            with open(filename, 'w' if rewrite else 'a') as file:
                yaml.dump(export_list, file)
            return True
        except (OSError, ValueError) as e:
            warnings.warn(e)
            return False

    @property
    def notes(self):
        return self._notes

    def get_note_idx_by_id(self, id_):
        idx = -1
        for i, note in enumerate(self._notes):
            if note.id_ == id_:
                idx = i
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

    def filter_notes(self, keys=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(keys, state)
        return [self._notes[i] for i in found_indexes] if found_indexes else []

    def delete_filtered(self, name=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(name, state)
        if not found_indexes:
            return False
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]
        return True

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


class NoteManagerCLI:
    def __init__(self, archive=""):
        self._archive_path = archive
        self._note_manager = NoteManager(NoteManager.import_yaml(self._archive_path)) \
            if self._archive_check(archive) else NoteManager([])

    @staticmethod
    def _nocturne(): # Дорогой дневник
        pygame.mixer.init()
        pygame.mixer.music.load("Chopin-NocturneNo1.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

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
                user_input = input(prompt).strip() if input_type != InputType.TEXT else curses.wrapper(femto, prompt)
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

    @staticmethod
    def _stop_nocturne():  # Дорогой дневник
        return pygame.mixer.music.stop()

    @classmethod
    def _start_nocturne(cls):  # Дорогой дневник
        audio_thread = threading.Thread(target=cls._nocturne)
        audio_thread.start()

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
                    self._start_nocturne()
                    note_args[key] = self._get_value_from_console(InputType.TEXT)
                    self._stop_nocturne()
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
        self._note_manager.add_note(note)
        self._save_note(note)
        print('\n', "Note created:", '\n')
        self._print_note_full(note)

    def _update_note(self):
        note_id = self._get_value_from_console(InputType.INT, "\nEnter the note ID to edit: ")
        i = self._note_manager.get_note_idx_by_id(note_id)
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
                        self._start_nocturne()
                        input_value = self._get_value_from_console(
                            InputType.TEXT,
                            self._note_manager.notes[i].content
                        )
                        self._stop_nocturne()
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


def main():
    if sys.stdout.isatty():
        colorama.init(autoreset=True)
        term = NoteManagerCLI("notes_stage_4.yaml")
        term.run()
    # Here is the place for GUI initialization
    return 0


if __name__ == "__main__":
    main()