import unittest
from uuid import UUID
from datetime import datetime, timedelta
from utils.helpers import str_to_date, date_to_str, generate_id
from utils.enums import NoteStatus


class TestHelpers(unittest.TestCase):
    def test_str_to_date_valid_date_future(self):
        # Test with a valid future date string
        future_date = (datetime.now() + timedelta(days=1)).strftime("%d-%m-%Y %H:%M")
        self.assertIsInstance(str_to_date(future_date), datetime)

    def test_str_to_date_valid_date_past(self):
        # Test with a valid past date string
        past_date = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y %H:%M")
        with self.assertRaises(ValueError):
            str_to_date(past_date)

    def test_date_to_str_non_deadline(self):
        # Test formatting when is_deadline is False
        date = datetime.now()
        formatted_date = date_to_str(date, is_deadline=False)
        self.assertEqual(formatted_date, date.strftime("%B %d, %Y %H:%M"))

    def test_date_to_str_deadline_termless(self):
        # Test with deadline and TERMLESS status
        date = datetime.now()
        formatted_date = date_to_str(date, is_deadline=True, state=NoteStatus.TERMLESS)
        self.assertEqual(formatted_date, "NO DEADLINE")


if __name__ == '__main__':
    unittest.main()