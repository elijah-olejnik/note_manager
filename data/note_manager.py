from dataclasses import asdict
from datetime import datetime
from utils.enums import NoteStatus
from utils.custom_exceptions import DataIntegrityError
from note import Note


class NoteManager:
    def __init__(self, notes):
        self._notes = notes if notes else []

    def __str__(self):
        return self._notes.__str__()

    @staticmethod
    def _from_dict(note_dict):
        try:
            note = Note(
                content=note_dict["content"],
                created_date=datetime.fromisoformat(note_dict["created_date"]),
                id_=note_dict["id_"],
                issue_date=datetime.fromisoformat(note_dict["issue_date"]),
                status=NoteStatus[note_dict["status"]],
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

    def import_from_dicts(self, note_dicts):
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

    def notes_as_dicts(self):
        return [asdict(note) for note in self._notes]

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

    def append_note(self, note):
        self._notes.append(note)

    def search_notes(self, keys=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(keys, state)
        return [self._notes[i] for i in found_indexes] if found_indexes else []

    def delete_filtered(self, keys=None, state=None):
        found_indexes = self._get_notes_idx_by_filter(keys, state)
        if not found_indexes:
            return False
        for i in sorted(found_indexes, reverse=True):
            del self._notes[i]
        return True

    def clear(self):
        if self._notes:
            self._notes.clear()

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