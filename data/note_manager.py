from utils import DataIntegrityError, NoteStatus, FileIOError
from data.file_io import export_to_yaml, import_from_yaml, export_to_json
from data.note import Note
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from uuid import UUID
import warnings


class NoteManager:
    """The NoteManager class represents a business-logic model
    handling the notes adding, storing, sorting, filtering,
    removing and the import/export routines.
    """
    def __init__(self):
        self._notes = []
        self.storage_path = Path("notes.yaml")
        self.load_notes_from_file()

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def _from_dict(note_dict):
        """The function converts dictionary loaded from JSON or
        YAML file to the Note class object and returns it.
        Raises DataIntegrityError if conversion fails.
        """
        required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
        if not all(field in note_dict for field in required_fields):
            raise DataIntegrityError(f"Missing required fields in record: {note_dict}")
        try:
            note = Note(
                content=note_dict["content"],
                created_date=datetime.fromisoformat(note_dict["created_date"]),
                id_=UUID(note_dict["id_"]),
                issue_date=datetime.fromisoformat(note_dict["issue_date"]),
                status=NoteStatus[note_dict["status"]], # noqa
                title=note_dict["title"],
                username=note_dict["username"]
            )
            return note
        except(ValueError, KeyError, TypeError) as e:
            raise DataIntegrityError(f"Data format error in record {note_dict}: {e}")

    @staticmethod
    def sort_notes(notes, by_created=True, descending=True):
        """The function sorts given list of notes by given bool arguments:

        1. If by_created is False, sorting is done by the issue_date.
        2. The list sorted descending (in case of date) goes from the newest note to the oldest one.
        """
        if not notes:
            return []
        return sorted(notes, key=lambda x: x.created_date, reverse=descending) if by_created else \
            sorted(notes, key=lambda x: (x.issue_date == datetime.min, x.issue_date), reverse=True)

    @property
    def notes(self):
        """The attribute gives access to the private list of Note objects stored in class."""
        return self._notes

    def _get_note_index_by_id(self, id_):
        """The function return an index of the note list element if note.id_ and the given id_ are equal.
        If no match found the function return -1.
        """
        idx = -1
        for i, note in enumerate(self._notes):
            if note.id_ == id_:
                idx = i
        return idx

    def _get_notes_indexes_by_filter(self, keys=None, status=None):
        """The function return a set of unique indexes filtered by keywords and/or status.

        The argument 'keys' takes a list of keywords.

        The argument 'status' takes a NoteStatus(Enum) value.
        """
        if not self._notes:
            return []
        filtered_indexes = set()
        for i, note in enumerate(self._notes):
            status_match = (status is None or note.status == status)
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

    def import_notes_from_dicts(self, note_dicts):
        """The function takes a list of dictionaries,
        loaded from JSON or YAML file and appends it to the _notes list as notes.
        Raises an exceptions if list is empty or if the dictionaries contain wrong data.
        """
        if not note_dicts:
            raise ValueError("Failed to import notes from dicts: it's empty.")
        for d in note_dicts:
            try:
                self._notes.append(self._from_dict(d))
            except DataIntegrityError as e:
                raise DataIntegrityError(f"Failed to import notes from dicts: {e}")

    def export_notes_as_dicts(self):
        """The function return a list of dictionaries converted from _notes for serialization purposes
        if the _notes list is not empty.
        """
        if self._notes:
            return [asdict(note) for note in self._notes] if self._notes else []

    def append_note(self, note):
        """The function takes a created note as an argument and appends it to the _notes list.
        Also, it appends a note to the file storage and raises a FileIOError exception if
        export to the file fails.
        """
        self._notes.append(note)
        try:
            export_to_yaml([asdict(note)], self.storage_path, False)
        except FileIOError as e:
            warnings.warn(e) # noqa

    def get_note_by_id(self, id_):
        """The function return a note by a given ID or
        raises a ValueError exception if id_ match not found.
        """
        for note in self._notes:
            if id_ == note.id_:
                return note
        raise ValueError(f"Note with ID {id_} not found.")

    def save_notes_to_file(self):
        """The function dumps _notes list to the file storage or raises an exception
        if export to the file failed.
        """
        try:
            export_to_yaml(self.export_notes_as_dicts(), self.storage_path)
        except (ValueError, FileIOError) as e:
            warnings.warn(e)

    def save_notes_json(self):
        """The function dumps _notes list to the file storage in JSON format or raises an exception
        if export to the file failed.
        """
        try:
            export_to_json(self.export_notes_as_dicts(), self.storage_path)
        except (ValueError, FileIOError) as e:
            warnings.warn(e)

    def load_notes_from_file(self):
        """The function load notes from the file storage or raises an exception when
        file IO or converting data to Note dataclass object fails.
        """
        if not self.storage_path.is_file():
            warnings.warn(f"File {self.storage_path} not found.")
            try:
                with open(self.storage_path, 'w'):
                    pass
                warnings.warn("A new file is created.")
            except OSError as e:
                warnings.warn(f"Can't create a new file: {e}")
            finally:
                warnings.warn("The note list is empty.")
        else:
            try:
                self.import_notes_from_dicts(import_from_yaml(self.storage_path))
            except (FileIOError, DataIntegrityError) as e:
                warnings.warn(e)

    def filter_notes(self, keys=None, state=None):
        """The function return a list of notes filtered by keywords and/or status.

        The argument 'keys' takes a list of keywords.

        The argument 'state' takes a NoteStatus(Enum) value.
        """
        found_indexes = self._get_notes_indexes_by_filter(keys, state)
        return [self._notes[i] for i in found_indexes] if found_indexes else []

    def delete_note_by_id(self, id_):
        """The function return a note popped from the _notes list by a given ID
        or raises a ValueError exception if no id_ match is found.
        """
        i = self._get_note_index_by_id(id_)
        if i == -1:
            raise ValueError(f"Note with ID {id_} not found.")
        return self._notes.pop(i)

    def delete_by_state(self, state):
        """The function delete _notes filtered by state.
        It takes a NoteStatus(Enum) value as an argument.
        """
        found_indexes = self._get_notes_indexes_by_filter(status=state)
        if not found_indexes:
            return False
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]
        return True

    def get_urgent_notes_sorted(self):
        """The function return a list of 3 lists of notes filtered by the deadline.
        Each note list in the list represents three levels of urgency:

        1. The list with the index 0 represents the notes with the missed deadline sorted by date ascending:
        the older - the closer to the beginning of the list.

        2. The list with the index 1 represents the notes with the deadline date which match the date
        the function is called.

        3. The list with the index 3 represents the notes with the deadline date which match the date
        the function is called + 1 day.

        If no notes match the filter condition of the corresponding urgency level the list will be empty (falsy).
        So, if no urgent notes at all – the function will return a list of 3 empty (falsy) lists.
        """
        if not self._notes:
            return None
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