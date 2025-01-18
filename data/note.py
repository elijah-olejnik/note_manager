from dataclasses import dataclass
from datetime import datetime
from utils.enums import NoteStatus

@dataclass
class Note:
    content: str
    created_date: datetime.date
    id_: str
    issue_date: datetime.date
    status: NoteStatus
    title: str
    username: str