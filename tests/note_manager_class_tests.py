import unittest
import uuid
from datetime import datetime, timedelta
from time import strptime
from unittest.mock import patch
from uuid import uuid4
from utils import NoteStatus
from data import Note, NoteManager


class TestNoteManager(unittest.TestCase):
    def setUp(self):
        self.note_manager = NoteManager()
        self.note_manager.delete_all()
        self.note_manager.storage_path = "test.yaml"
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
        self.note_manager.import_notes_from_dicts(self.note_dicts)
        notes_as_dicts = self.note_manager.export_notes_as_dicts()
        for d in notes_as_dicts:
            d['id_'] = str(d['id_'])
            d['status'] = d['status'].name
            d['created_date'] = d['created_date'].isoformat()
            d['issue_date'] = d['issue_date'].isoformat()
        self.assertEqual(self.note_dicts, notes_as_dicts)


if __name__ == '__main__':
    unittest.main()

