import unittest
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4
from data.note import Note
from data.note_manager import NoteManager, NoteStatus


class TestNoteManager(unittest.TestCase):
    def setUp(self):
        self.note_manager = NoteManager()
        self.note_manager._notes = []

    def test_append_note(self):
        note = Note(
            title="Test Note",
            content="This is a test note.",
            username="tester",
            created_date=datetime.now(),
            issue_date=datetime.now(),
            status=NoteStatus.ACTIVE,
            id_=uuid4()
        )

        with patch('note_manager.data.note_manager.export_to_yaml') as mock_export:
            self.note_manager.append_note(note)
            self.assertIn(note, self.note_manager._notes)
            mock_export.assert_called_once()

    def test_get_note_by_id_found(self):
        note = Note(
            title="Test Note",
            content="This is a test note.",
            username="tester",
            created_date=datetime.now(),
            issue_date=datetime.now(),
            status=NoteStatus.ACTIVE,
            id_=uuid4()
        )
        self.note_manager._notes.append(note)
        found_note = self.note_manager.get_note_by_id(note.id_)
        self.assertEqual(found_note, note)

    def test_get_note_by_id_not_found(self):
        with self.assertRaises(ValueError):
            self.note_manager.get_note_by_id(uuid4())

    def test_delete_note_by_id(self):
        note_id = uuid4()
        note = Note(
            title="Test Note",
            content="This is a test note.",
            username="tester",
            created_date=datetime.now(),
            issue_date=datetime.now(),
            status=NoteStatus.ACTIVE,
            id_=note_id
        )
        self.note_manager._notes.append(note)
        deleted_note = self.note_manager.delete_note_by_id(note_id)
        self.assertNotIn(note, self.note_manager._notes)
        self.assertEqual(deleted_note, note)

    def test_delete_note_by_id_not_found(self):
        with self.assertRaises(ValueError):
            self.note_manager.delete_note_by_id(uuid4())

    def test_load_notes_from_file_empty_file(self):
        with patch('note_manager.data.note_manager.Path.is_file', return_value=False), \
             patch('note_manager.data.note_manager.warnings.warn') as mock_warn:
            self.note_manager.load_notes_from_file()
            mock_warn.assert_called()

    def test_save_notes_to_file(self):
        with patch('note_manager.data.note_manager.export_to_yaml') as mock_export:
            self.note_manager.save_notes_to_file()
            mock_export.assert_called_once()

    def test_filter_notes(self):
        note = Note(
            title="Important Note",
            content="Urgent matter.",
            username="user123",
            created_date=datetime.now(),
            issue_date=datetime.now() + timedelta(days=1),
            status=NoteStatus.ACTIVE,
            id_=uuid4()
        )
        self.note_manager._notes.append(note)
        filtered_notes = self.note_manager.filter_notes(keys=["Important", "urgent"], state=NoteStatus.ACTIVE)
        self.assertIn(note, filtered_notes)


if __name__ == '__main__':
    unittest.main()

