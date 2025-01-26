import unittest
from database import setup_db, save_note_to_db, load_notes_from_db
from datetime import datetime, timedelta
from utils import NoteStatus


class TestNoteDatabase(unittest.TestCase):
    def setUp(self):
        self.dbpath = 'test.db'
        setup_db(self.dbpath)
        self.test_note = {
            'username': "tester",
            'title': "db test",
            'content': "this is the test note for test.db",
            'status': NoteStatus.ACTIVE,
            'created_date': datetime.now().date(),
            'issue_date' : (datetime.now() + timedelta(weeks=1)).date()
        }

    def test_db_save_load_note(self):
        save_note_to_db(self.test_note, self.dbpath)
        loaded_note = load_notes_from_db(self.dbpath)[0]
        del loaded_note['id_']
        self.assertEqual(self.test_note, loaded_note)


if __name__ == '__main__':
    unittest.main()
