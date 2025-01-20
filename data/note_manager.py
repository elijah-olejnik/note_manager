from utils import DataIntegrityError, NoteStatus, FileIOError
from data import Note, export_to_yaml, import_from_yaml, export_to_json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from uuid import UUID
import warnings


class NoteManager:
    def __init__(self):
        self._notes = []
        self.storage_path = Path("notes.yaml")
        self.load_notes_from_file()

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def _from_dict(note_dict):
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
        if not notes:
            return []
        return sorted(notes, key=lambda x: x.created_date, reverse=descending) if by_created else \
            sorted(notes, key=lambda x: (x.issue_date == datetime.min, x.issue_date), reverse=True)

    @property
    def notes(self):
        return self._notes

    def _get_notes_indexes_by_filter(self, keys=None, status=None):
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
        if not note_dicts:
            raise ValueError("Failed to import notes from dicts: it's empty.")
        required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
        for d in note_dicts:
            if not all(field in d for field in required_fields):
                raise DataIntegrityError(f"Missing required fields in record: {d}")
            try:
                self._notes.append(self._from_dict(d))
            except DataIntegrityError as e:
                raise DataIntegrityError(f"Failed to import notes from dicts: {e}")

    def export_notes_as_dicts(self):
        return [asdict(note) for note in self._notes] if self._notes else []

    def get_note_index_by_id(self, id_):
        idx = -1
        for i, note in enumerate(self._notes):
            if note.id_ == id_:
                idx = i
        return idx

    def append_note(self, note):
        self._notes.append(note)
        try:
            export_to_yaml([asdict(note)], "", False)
        except FileIOError as e:
            warnings.warn(e.__str__())

    def save_notes_to_file(self):
        try:
            export_to_yaml(self.export_notes_as_dicts(), self.storage_path)
        except (ValueError, FileIOError) as e:
            warnings.warn(e.__str__)

    def save_notes_json(self):
        try:
            export_to_json(self.export_notes_as_dicts(), self.storage_path)
        except (ValueError, FileIOError) as e:
            warnings.warn(e.__str__)

    def load_notes_from_file(self):
        if not self.storage_path.is_file():
            warnings.warn(f"File {self.storage_path} wasn't found.")
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
                self._notes = self.import_notes_from_dicts(import_from_yaml(self.storage_path))
            except (FileIOError, DataIntegrityError) as e:
                warnings.warn(e.__str__)

    def filter_notes(self, keys=None, state=None):
        found_indexes = self._get_notes_indexes_by_filter(keys, state)
        return [self._notes[i] for i in found_indexes] if found_indexes else []

    def delete_by_state(self, state):
        found_indexes = self._get_notes_indexes_by_filter(status=state)
        if not found_indexes:
            return False
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]
        return True

    def get_urgent_notes_sorted(self):
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