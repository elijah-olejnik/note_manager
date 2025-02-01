from enum import Enum


class NoteStatus(Enum):
    """The enum NoteStatus represents the status of the note."""
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


class InputType(Enum):
    """The enum InputType is needed for
    user input handling convenience.
    """
    INT = 0
    STR = 1
    TEXT = 2
    ENUM_VAL = 3
    DATE = 4
