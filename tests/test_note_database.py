import sqlite3
import unittest
from unittest.mock import patch, MagicMock
from database import *
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

    @patch('sqlite3.connect')
    def test_update_note(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = mock_conn.cursor.return_value
        mock_connect.return_value.__enter__.return_value = mock_conn
        note_id = 1
        updates = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': NoteStatus.COMPLETED,
            'issue_date': datetime.now() + timedelta(weeks=1)
        }
        db_path = ':memory:'
        update_note_in_db(note_id, updates, db_path)
        mock_cursor.execute.assert_called_once_with(
            """UPDATE notes SET title = ?, content = ?, status = ?, issue_date = ? WHERE id = ?;""",
            data_from_note(updates, note_id)
        )
        mock_conn.commit.assert_called_once()

    @patch('sqlite3.connect')
    def test_update_note_failure(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.side_effect = sqlite3.Error("Some error")
        note_id = 1
        updates = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': NoteStatus.TERMLESS,
            'issue_date': datetime.now() + timedelta(weeks=1)
        }
        db_path = ':memory:'
        with self.assertRaises(DatabaseError) as context:
            update_note_in_db(note_id, updates, db_path)
        self.assertEqual(str(context.exception), "Updating note in db failed: Some error")
        mock_conn.rollback.assert_called_once()

    @patch('sqlite3.connect')
    def test_delete_note_successful(self, mock_connect):
        mock_conn = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_cursor = mock_conn.cursor.return_value
        delete_note_from_db(note_id=1, db_path='fake_path.db')
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with("DELETE FROM notes WHERE id = ?;", (1,))
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
