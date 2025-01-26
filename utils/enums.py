from enum import Enum


class NoteStatus(Enum):
    """The enum NoteStatus represents the status of the note."""
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3
