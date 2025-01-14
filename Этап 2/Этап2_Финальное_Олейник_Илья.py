import curses
import dataclasses
from datetime import datetime
import json
import random
import re
from enum import Enum
from typing import Tuple, Union
import femto  # My tiny console editor

divider = "_" * 30  # The divider for console output


# note status as Enum for convenience
class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3


# I think the data class would be better and more extendable
# but the dictionary functionality remained the same
@dataclasses.dataclass
class Note:
    id_: int = random.randint(10000, 99999)
    username: str = ""
    titles: list = dataclasses.field(default_factory=list)
    content: str = ""
    status: Status = Status.TERMLESS
    created_date: datetime.date = datetime.now()
    issue_date: datetime.date = datetime.min

    def __init__(self, note_dict=None):
        self.titles = []  # Had to add this because of field doesn't exist error
        if isinstance(note_dict, dict):
            self.add_from_dictionary(note_dict)

    def as_dictionary(self):
        return {
            "id": self.id_,
            "username": self.username,
            "titles": self.titles,
            "content": self.content,
            "status": self.status,
            "created_date": self.created_date,
            "issue_date": self.issue_date
        }

    def add_from_dictionary(self, note_dic):
        self.id_ = int(note_dic["id"])
        self.username = note_dic["username"]
        self.titles = note_dic["titles"]
        self.content = note_dic["content"]
        self.status = note_dic["status"]
        self.created_date = note_dic["created_date"]
        self.issue_date = note_dic["issue_date"]

    def __str__(self):
        date_display_fmt: str = "%B %d, %Y %H:%M"
        return (
            f"\n\nNote ID #{self.id_}\n\n"
            f"Username: {self.username}\n"
            f"{"\n".join("Title " + str(i + 1) + ": " + title for i, title in enumerate(self.titles))}\n"
            f"Content: \n{self.content.replace('{{', '').replace('}}', '')}\n\n"
            f"Status: {self.status.name}\n"
            f"Created: {datetime.strftime(self.created_date, date_display_fmt)}\n"
            f"Deadline: {datetime.strftime(self.issue_date, date_display_fmt)
            if self.status != Status.TERMLESS else "no deadline"}\n"
        )


# Custom JSON encoder for easy datetime and Status(Enum) conversion
class NoteEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.name
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj


# The JSON decoder function
def note_decoder(obj):
    obj["status"] = Status[obj["status"]]
    obj["created_date"] = datetime.fromisoformat(obj["created_date"])
    try:
        obj["issue_date"] = datetime.fromisoformat(obj["issue_date"])
    except ValueError:
        pass
    return obj


# This function extracts marked titles out of the text
# or make a title from the first words if no marked titles provided
def _extract_titles(text):
    headers = re.findall(r'\{\{(.*?)}}', text)
    if not headers:
        headers = []
        words = text.split()
        if len(words) == 1:
            headers.append(words[0])
        elif len(words) == 2:
            headers.append(" ".join(words[:2]))
        else:
            headers.append(" ".join(words[:3]))
    return headers


# NoteManager itself
class NoteManager:
    _in_date_fmts = ("%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M")
    def __init__(self):
        self._notes = []
        self._load_from_json()

    def notes_count(self):
        return len(self._notes)

    def _load_from_json(self):
        try:
            with open("../notes.json") as f:
                import_list = json.loads(f.read(), object_hook=note_decoder)
            for note_dic in import_list:
                note = Note(note_dic)
                self._notes.append(note)
        except (OSError, ValueError) as e:
            print("Couldn't open/read notes.json:", e)

    def _save_to_json(self):
        export_list = []
        for note in self._notes:
            export_list.append(note.as_dictionary())
        try:
            with open("../notes.json", 'w') as file_:
                file_.write(json.dumps(export_list, cls=NoteEncoder, indent=4))
        except (ValueError, OSError) as e:
            print("The note manager can't save changes:", e)

    def delete_note(self, idx):
        del self._notes[idx]
        if self.notes_count() > 0:
            self._save_to_json()

    # The deadline check
    def get_urgent_notes_info(self):
        missed_dl = []
        today_dl = []
        oneday_dl = []
        for note in self._notes:
            if note.status != Status.TERMLESS:
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

    def _is_date_acceptable(self, str_date="", is_issue_date=False) -> Tuple[bool, Union[datetime, ValueError]]:
        for fmt in self._in_date_fmts:
            try:
                date = datetime.strptime(str_date, fmt)
                if is_issue_date:
                    return True, date
                else:
                    if date.date() != datetime.today().date():
                        print("\nWhat are you hiding, cheater? =)")
                    return True, date
            except ValueError as e:
                return False, e

    def add_from_console(self):
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
        note = Note()
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

    # Search functions
    def get_notes_indexes_by_keys(self, keys):
        notes_found = set()
        for i, note in enumerate(self._notes):
            for key in keys:
                if key[0] == " ":
                    ey = key[1:]
                    key = ey
                if key.isdigit() and int(key) == note.id_:
                    notes_found.add(i)
                elif key.lower() in note.username.lower():
                    notes_found.add(i)
                elif key.lower() in note.content.lower():
                    notes_found.add(i)
        return notes_found

    def get_note_idx_by_id(self, id_):
        idx = -1
        for i, note in enumerate(self._notes):
            if note.id_ == id_:
                idx = i
        return idx

    def get_note_by_idx(self, i):
        return self._notes[i]

    def edit_note_in_console(self):
        i = 0
        while True:
            note_id = input("Enter the note id or 'm' to return to the main menu: ")
            if not note_id.isdigit():
                if note_id == 'm':
                    return
                else:
                    continue
            i = self.get_note_idx_by_id(int(note_id))
            if i == -1:
                print("\nNo such note!")
                continue
            else:
                break
        while True:
            print(self._notes[i])
            command = input(
                "Choose what to edit:\n"
                "'0' - Username\n"
                "'1' - Note text\n"
                "'2' - Note state\n"
                "'3' - Deadline\n"
                "'4' - Delete note\n"
                "'5' - Return to the main menu\n\n"
                "Enter the number: "
            )
            match command:
                case '0':
                    while True:
                        username = input("Enter new username: ")
                        if not username:
                            continue
                        self._notes[i].username = username
                        self._save_to_json()
                        break
                case '1':
                    edited_text = curses.wrapper(femto.femto, self._notes[i].content)
                    if not edited_text:
                        continue
                    self._notes[i].content = edited_text
                    self._notes[i].titles = _extract_titles(edited_text)
                    self._save_to_json()
                case '2':
                    print(
                        f"\nThe current note state is {self._notes[i].status.name}\n"
                        "Choose the new state:\n\n"
                        "0 or active for ACTIVE\n"
                        "1 or completed for COMPLETED\n"
                        "2 or completed for TERMLESS\n"
                        "3 or postponed for POSTPONED\n"
                    )
                    while True:
                        user_input = input("\nSwitch state to: ").lower()
                        if user_input in (self._notes[i].status.name.lower(), str(self._notes[i].status.value)):
                            print(f"The note state remained the same: {self._notes[i].status.name}")
                            break
                        match user_input:
                            case '0' | 'active':
                                self._notes[i].status = Status.ACTIVE
                            case '1' | 'completed':
                                self._notes[i].status = Status.COMPLETED
                            case '2' | 'termless':
                                self._notes[i].status = Status.TERMLESS
                            case '3' | 'postponed':
                                self._notes[i].status = Status.POSTPONED
                            case _:
                                print("Try again")
                                continue
                        self._save_to_json()
                        break
                case '3':
                    while True:
                        user_input = input("Enter the deadline date in 'dd-mm-yyyy' or 'yyyy-mm-dd' format: ")
                        result = self._is_date_acceptable(user_input, True)
                        if result[0]:
                            if result[1] < self._notes[i].created_date:
                                print("\nThe deadline date of a note can't be "
                                      "earlier than the date it was created!")
                                continue
                            self._notes[i].issue_date = result[1]
                        else:
                            print("\n", result[1])
                            continue
                        self._save_to_json()
                        break
                case '4':
                    self.delete_note(i)
                    break
                case '5':
                    break

    def __str__(self):
        output_string = ""
        for i, note in enumerate(self._notes):
            output_string += note.__str__() + divider  # Can't concatenate note + str!? WTF?
        return output_string


# main() function
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
                print(divider)
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