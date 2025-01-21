import unittest
from unittest.mock import mock_open, patch
from datetime import datetime
from uuid import UUID
from data import import_from_yaml, import_from_json, export_to_yaml, export_to_json
from utils import FileIOError, NoteStatus


class TestFileIO(unittest.TestCase):
    def test_import_from_yaml_valid(self):
        mock_data = """
        - id: !!python/str '123e4567-e89b-12d3-a456-426614174000'
          created_at: 2021-01-01T12:00:00
          status: ACTIVE
          content: 'Sample note content'
        """
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch('yaml.safe_load', return_value=[{'id': '123e4567-e89b-12d3-a456-426614174000', 'created_at': datetime(2021, 1, 1, 12, 0), 'status': 'ACTIVE', 'content': 'Sample note content'}]):
                result = import_from_yaml('dummy.yaml')
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['content'], 'Sample note content')

    def test_import_from_yaml_empty(self):
        with patch('builtins.open', mock_open(read_data="")):
            with patch('yaml.safe_load', return_value=None):
                with self.assertRaises(FileIOError):
                    import_from_yaml('dummy.yaml')

    def test_export_to_yaml_valid(self):
        data = [{'id': UUID('123e4567-e89b-12d3-a456-426614174000'), 'created_at': datetime.now(), 'status': NoteStatus.ACTIVE, 'content': 'Sample note'}]
        m = mock_open()
        with patch('builtins.open', m):
            export_to_yaml(data, 'dummy.yaml')
        m.assert_called_once()

    def test_export_to_yaml_empty(self):
        with self.assertRaises(ValueError):
            export_to_yaml([], 'dummy.yaml')

    def test_import_from_json_valid(self):
        mock_data = '[{"id": "123e4567-e89b-12d3-a456-426614174000", "created_at": "2021-01-01T12:00:00", "status": "ACTIVE", "content": "Sample note content"}]'
        with patch('builtins.open', mock_open(read_data=mock_data)):
            with patch('json.load', return_value=[{'id': '123e4567-e89b-12d3-a456-426614174000', 'created_at': '2021-01-01T12:00:00', 'status': 'ACTIVE', 'content': 'Sample note content'}]):
                result = import_from_json('dummy.json')
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['content'], 'Sample note content')

    def test_import_from_json_empty(self):
        with patch('builtins.open', mock_open(read_data="[]")):
            with patch('json.load', return_value=[]):
                with self.assertRaises(FileIOError):
                    import_from_json('dummy.json')

    def test_export_to_json_valid(self):
        data = [{'id': UUID('123e4567-e89b-12d3-a456-426614174000'), 'created_at': datetime.now(), 'status': NoteStatus.ACTIVE, 'content': 'Sample note'}]
        m = mock_open()
        with patch('builtins.open', m):
            export_to_json(data, 'dummy.json')
        m.assert_called_once()

    def test_export_to_json_empty(self):
        with self.assertRaises(ValueError):
            export_to_json([], 'dummy.json')


if __name__ == '__main__':
    unittest.main()