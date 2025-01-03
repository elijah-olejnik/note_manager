import dataclasses
from datetime import datetime
import json
import random
import re
import readline
from enum import Enum
from typing import Tuple, Union


class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3

def prefill_input(prompt, text):
    readline.set_startup_hook(lambda: readline.insert_text(text))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()

@dataclasses.dataclass
class Note:
    username: str = ""
    content: str = ""
    status: Status = Status.TERMLESS
    created_date: datetime.date = dataclasses.field(default_factory=datetime.now)
    issue_date: datetime.date = dataclasses.field(default_factory=lambda: datetime.min)
    titles: list = dataclasses.field(default_factory=list)
    _id: int = random.randint(10000, 99999)

    @property
    def id(self) -> int:
        return self._id

    def as_dictionary(self):
        return {
            "id": self._id,
            "username": self.username,
            "titles": self.titles,
            "content": self.content,
            "status": self.status,
            "created_date": self.created_date,
            "issue_date": self.issue_date
        }

    def add_from_dictionary(self, note_dic):
        self._id = note_dic["id"]
        self.username = note_dic["username"]
        self.titles = note_dic["titles"]
        self.content = note_dic["content"]
        self.status = note_dic["status"]
        self.created_date = note_dic["created_date"]
        self.issue_date = note_dic["issue_date"]

    def __str__(self):
        date_display_fmt: str = "%B %d, %Y %H:%M"
        return (
            f"\n\nNote ID #{self._id}\n\n"
            f"Username: {self.username}\n"
            f"{"\n".join("Title " + str(i+1) + ": " + title for i, title in enumerate(self.titles))}\n"
            f"Content: \n{self.content}\n\n"
            f"Status: {self.status.name}\n"
            f"Created: {datetime.strftime(self.created_date, date_display_fmt)}\n"
            f"Deadline: {datetime.strftime(self.issue_date, date_display_fmt)
            if self.status != Status.TERMLESS else "no deadline"}\n"
        )

class NoteEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Enum):
            return o.name
        elif isinstance(o, datetime):
            return o.isoformat()
        else:
            return o

class NoteManager:
    _in_date_fmts = ("%d-%m-%Y %H:%M", "%Y-%m-%d %H:%M", "%d.%m.%Y %H:%M", "%d/%m/%Y %H:%M")
    _regexp = r'\{\{(.*?)\}\}'
    _prompts = (
        'Enter your name', 'Enter your note. If you want to add a title,\nor an additional '
                           'titles/headers within your text,\nuse double curly braces, e.g. {{Some title}}.'
                           '\nUse Enter key to add a new line,\nor type "end" to finish the note input\n',
        'Enter the note state: type "a" if ACTIVE, "c" if COMPLETED, "p" if POSTPONED '
        'or skip pressing Enter if TERMLESS',
        f'Enter the date and time of note creation or press Enter for auto input\nAcceptable formats:\n'
        f'{"\n".join(_in_date_fmts)}\n\nCreated',
        'Enter the date and time of the note deadline or press Enter if termless\nAcceptable formats:\n'
        f'{"\n".join(_in_date_fmts)}\n\nDeadline'
    )

    def __init__(self):
        self._notes = []

    def has_notes(self):
        if len(self._notes) < 1:
            return False
        return True

    def _is_date_accepted(self, str_date = "", is_issue_date = False) -> Tuple[bool, Union[datetime, ValueError]]:
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
        note = Note()
        for i, prompt in enumerate(self._prompts):
            while True:
                user_input = input("\n"
                                   + prompt
                                   + (f" (today is {datetime.strftime(note.created_date, self._in_date_fmts[0])}): "
                                   if i == 3 else ": "))
                if i < 2 and not user_input:
                    continue
                match i:
                    case 0:
                        note.username = user_input
                    case 1:
                        while True:
                            new_line = input()
                            if new_line.lower() == "end":
                                break
                            user_input += "\n" + new_line
                        headers = re.findall(self._regexp, user_input)
                        if headers:
                            note.titles = headers
                            note.content = re.sub(self._regexp, r'\n\1\n', user_input)
                        else:
                            note.content = user_input
                            words = user_input.split()
                            if len(words) == 1:
                                note.titles .append(words[0])
                            elif len(words) == 2:
                                note.titles .append(" ".join(words[:2]))
                            else:
                                note.titles .append(" ".join(words[:3]))
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
                        result = self._is_date_accepted(user_input, i == 4)
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
        print("\nYour note is successfully saved\n")

    def __str__(self):
        output_string = ""
        for i, note in enumerate(self._notes):
            output_string += note + ("_" * 30)
        return output_string

    def delete_note(self, key):
        if key.isdigit():
            id_ = int(key)
            for i, note in enumerate(self._notes):
                if note.id == id_:
                    self._notes.pop(i)
                    return True
        else:
            for i, note in enumerate(self._notes):
                if key in note["titles"][0]:
                    self._notes.pop(i)
                    return True
        return False

    def _save_to_json(self):
        try:
            with open("notes.json", 'w') as file_:
                file_.write(json.dumps(self._notes, cls = NoteEncoder, indent = 4))
        except (ValueError, OSError) as e:
            print("The note manager can't save changes:", e)

    # def _load_from_json(self): TODO

note_manager = NoteManager()

print("\n", "Welcome to the note manager!\n")

while True:
    command = input("Enter 'n' for a new note, 'd' to delete one or 'q' for quit: ")
    match command:
        case 'q':
            break
        case 'd':
            if not note_manager.has_notes():
                print("\nNo notes yet")
                continue
            print("\nHere are your notes:", note_manager)
            while True:
                user_key = input("Enter an ID or the title of the note to delete: ")
                if not note_manager.delete_note(user_key):
                    print(f"The note {user_key} not found!")
                    continue
                print(f"\nThe note {user_key} is successfully deleted")
        case 'n':
            note_manager.add_from_console()
        case _:
            print(f"{command} is not a command")
            continue

print("\nHere are your notes:", note_manager)

# if note_manager.is_json_saved():
#     print("File saved")