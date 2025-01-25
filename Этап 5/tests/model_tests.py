import unittest
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4
from data import NoteManager
from utils import NoteStatus


class TestNoteManager(unittest.TestCase):
    def setUp(self):
        self.note_manager = NoteManager()
        if self.note_manager.notes:
            self.note_manager._notes.clear()
        self.note_manager.storage_path = Path("test.yaml")
        self.note_dicts = [
            {
                'id_' : str(uuid4()),
                'username' : 'Tester',
                'title' : 'Test',
                'content' : 'Test content for unit tests',
                'status' : NoteStatus.ACTIVE.name,
                'created_date' : datetime.now().isoformat(),
                'issue_date' : (datetime.now() + timedelta(days=5)).isoformat(),
            },
            {
                'id_': str(uuid4()),
                'username': 'Tester2',
                'title': 'Test2',
                'content': 'Test content2 for unit tests',
                'status': NoteStatus.ACTIVE.name,
                'created_date': datetime.now().isoformat(),
                'issue_date': (datetime.now() + timedelta(days=1)).isoformat(),
            }
        ]

    def test_dict_import_export(self):
        # Testing a dict-Note-Note-dict converting functions
        self.note_manager.import_notes_from_dicts(self.note_dicts)
        dicts_from_note_manager = self.note_manager.export_notes_as_dicts()
        for d in dicts_from_note_manager:
            d['id_'] = str(d['id_'])
            d['status'] = d['status'].name
            d['created_date'] = d['created_date'].isoformat()
            d['issue_date'] = d['issue_date'].isoformat()
        self.assertEqual(self.note_dicts, dicts_from_note_manager)

    def test_save_and_load_notes(self):
        # Testing a save/load to/from a file and converting functions
        self.note_manager.import_notes_from_dicts(self.note_dicts)
        self.note_manager.save_notes_to_file()
        self.note_manager._notes.clear()
        self.note_manager.load_notes_from_file()
        dicts_from_note_manager = self.note_manager.export_notes_as_dicts()
        for d in dicts_from_note_manager:
            d['id_'] = str(d['id_'])
            d['status'] = d['status'].name
            d['created_date'] = d['created_date'].isoformat()
            d['issue_date'] = d['issue_date'].isoformat()
        self.assertEqual(self.note_dicts, dicts_from_note_manager)

    def test_delete_by_id(self):
        # Testing note deletion that should pop() the note from list and return it
        self.note_manager.import_notes_from_dicts(self.note_dicts)
        self.note_manager.save_notes_to_file()
        note_orig = self.note_manager._from_dict(self.note_dicts[1])
        note_popped = self.note_manager.delete_note_by_id(self.note_manager.notes[1].id_)
        self.assertEqual(note_orig, note_popped)

    def test_get_note_by_id(self):
        # Testing getting a note from notes list by UUID
        self.note_manager.import_notes_from_dicts(self.note_dicts)
        test_note = self.note_manager.notes[0]
        id_ = test_note.id_
        self.assertEqual(test_note, self.note_manager.get_note_by_id(id_))


if __name__ == '__main__':
    unittest.main()
