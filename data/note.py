from utils import NoteStatus
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class Note:
    content: str
    created_date: datetime
    id_: UUID
    issue_date: datetime
    status: NoteStatus
    title: str
    username: str