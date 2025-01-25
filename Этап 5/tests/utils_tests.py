import unittest
from datetime import datetime, timedelta
from utils import str_to_date, date_to_str, input_to_enum_value
from utils import NoteStatus


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

    def test_string_input(self):
        # Test correct string input
        self.assertEqual(input_to_enum_value("active", NoteStatus), NoteStatus.ACTIVE)
        self.assertEqual(input_to_enum_value("completed", NoteStatus), NoteStatus.COMPLETED)

        # Test incorrect string input (expecting exception)
        with self.assertRaises(ValueError) as context:
            input_to_enum_value("purple", NoteStatus)
        self.assertIn("Not an Enum value", str(context.exception))

    def test_digit_string_input(self):
        # Test correct digit input as string
        self.assertEqual(input_to_enum_value("1", NoteStatus), NoteStatus.COMPLETED)
        self.assertEqual(input_to_enum_value("2", NoteStatus), NoteStatus.POSTPONED)

        # Test incorrect digit input as string (expecting exception)
        with self.assertRaises(ValueError) as context:
            input_to_enum_value("4", NoteStatus)
        self.assertIn("Not an Enum value", str(context.exception))


if __name__ == '__main__':
    unittest.main()
