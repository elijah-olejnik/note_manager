import curses
import dataclasses
import yaml
import colorama
from colorama import Style, Fore
from random import randint
from datetime import datetime
from enum import Enum
from pathlib import Path
from femto import femto  # My tiny console editor


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


@dataclasses.dataclass
class Note:
    username: str
    title: str
    content: str
    status: NoteStatus
    issue_date: datetime.date
    id_: int = randint(10000, 99999)
    created_date: datetime.date = datetime.now()


class NoteManager:
    def __init__(self, archive = "notes.yaml", datetime_fmt = "%d-%m-%Y %H:%M"):
        yaml.add_representer(datetime, self.datetime_representer)
        yaml.add_representer(NoteStatus, self.enum_representer)
        self._notes = []
        self._datetime_fmt = datetime_fmt
        self._archive_path = archive
        if self.archive_check(archive):
            self._notes = self.import_yaml(self._archive_path)

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def archive_check(pathname):
        archive = Path(pathname)
        if archive.is_file() and archive.stat().st_size > 0:
            return True
        return False

    @staticmethod
    def str_to_deadline(str_date, fmt):
        date = datetime.strptime(str_date, fmt)
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date

    @staticmethod
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())

    @staticmethod
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)

    @staticmethod
    def import_yaml(filename):
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

    def export_yaml(self, filename):
        if len(self._notes) > 0:
            export_list = [dataclasses.asdict(note) for note in self._notes]
            with open(filename, 'w') as file:
                yaml.dump(export_list, file)

    @property
    def archive_path(self):
        return self._archive_path

    @archive_path.setter
    def archive_path(self, archive):
        self._archive_path = archive
        if self.archive_check(archive):
            self._notes = self.import_yaml(self._archive_path)

    @property
    def datetime_fmt(self):
        return self._datetime_fmt

    @datetime_fmt.setter
    def datetime_fmt(self, fmt):
        self._datetime_fmt = fmt

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

    def delete_note(self, id_):
        i = self._get_note_idx_by_id(id_)
        del self._notes[i]
        self.export_yaml(self._archive_path)

    def delete_filtered(self, name=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(name, state)
        if not found_indexes:
            raise KeyError("Can't delete non-existing notes")
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]
        self.export_yaml(self._archive_path)

    def clear(self):
        if len(self._notes) > 0:
            self._notes.clear()

    # The deadline check
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
        output_string = ""
        missed_count = len(missed_dl)
        today_count = len(today_dl)
        oneday_count = len(oneday_dl)
        if missed_count > 0:
            output_string += (
                    "Notes with missed deadline: " + str(missed_count) + "\n"
                    + "\n".join(note_info[0].titles[0] + " #" + str(note_info[0].id_)
                                + ", " + str(abs(note_info[1])) + " days after deadline" for note_info in missed_dl)
            )
            output_string += "\n"
        if today_count > 0:
            output_string += (
                    "Notes which deadline is today: " + str(today_count) + "\n"
                    + "\n".join(note.titles[0] + " " + str(note.id_) for note in today_dl) + "\n"
            )
        if oneday_count > 0:
            output_string += (
                    "Notes which deadline is tomorrow: " + str(oneday_count) + "\n"
                    + "\n".join(note.titles[0] + " " + str(note.id_) for note in oneday_dl) + "\n"
            )
        urg_notes: list[Note] = []
        for missed in missed_dl:
            urg_notes.append(missed[0])
        for today in today_dl:
            urg_notes.append(today)
        for oneday in oneday_dl:
            urg_notes.append(oneday)
        return output_string, urg_notes


class InputType(Enum):
    INT = 0
    STR = 1
    TEXT = 2
    ENUM_VAL = 3
    DATE = 4


class TerminalInterface:
    def __init__(self, note_manager = NoteManager()):
        self._note_manager = note_manager

    @staticmethod
    def user_confirmation():
        while True:
            user_input = input("Are you sure? y|n: ")
            if user_input == 'y':
                return True
            elif user_input == 'n':
                return False
            else:
                pass

    @staticmethod
    def print_note_full(note):
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
    def print_note_short(note):
        print(f"{Fore.CYAN}Note ID #{Style.RESET_ALL}{note.id_}: {note.title}\n\n")

    def get_value_from_console(self, input_type, prompt="", enum_=None):
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
                        return self._note_manager.str_to_deadline(user_input, self._note_manager.datetime_fmt)
                    case _:
                        return user_input
            except (KeyError, ValueError) as e:
                print('\n', e, '\n')


def main():
    note_manager = NoteManager()
    print("\n", "Welcome to the note manager!\n")
    notes_count = note_manager.notes_count()
    if notes_count > 0:
        print(f"{notes_count}", "notes" if notes_count > 1 else "note", "found")
    urgent = note_manager.get_urgent_notes_info()
    if urgent[0]:
        print(urgent[0])
        choice = input("View this notes? y | n: ")
        if choice == 'y':
            for urg_note in urgent[1]:
                print(urg_note)
    while True:
        print("\nn - new note")
        print("a - view all notes")
        print("s - search/vew note(s)")
        print("e - edit or delete note")
        print("q - quit\n")
        command = input("Enter a command: ")
        match command:
            case 'q':
                break
            case 'a':
                print("\nHere are your notes:", note_manager)
            case 's':
                keywords = input("Enter a username, titles, keywords or IDs separated by ';'\n"
                                 "or leave blank to return to the main menu: ").split(";")
                if not keywords:
                    break
                found = note_manager.get_notes_indexes_by_keys(keywords)
                if len(found) > 0:
                    for i in found:
                        print(note_manager.get_note_by_idx(i))
                else:
                    print("\nNo matches found")
            case 'e':
                note_manager.edit_note_in_console()
            case 'n':
                note_manager.add_from_console()
            case _:
                print(f"{command} is not a command")


if __name__ == "__main__":
    main()