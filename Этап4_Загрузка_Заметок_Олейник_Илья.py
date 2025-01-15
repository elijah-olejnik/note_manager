import yaml
from datetime import datetime
from enum import Enum


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


def load_notes_from_file(filename):
    try:
        with open(filename, 'r') as file:
            import_list = yaml.safe_load(file)
        if not import_list:
            raise ValueError(f"File {filename} is empty!")
        return [
            {
                "content" : d["content"],
                "created_date" : datetime.fromisoformat(d["created_date"]),
                "id_" : d["id_"],
                "issue_date" : datetime.fromisoformat(d["issue_date"]),
                "status" : NoteStatus[d["status"]],
                "title" : d["title"],
                "username" : d["username"]
            } for d in import_list
        ]
    except (OSError, ValueError) as e:
        print("\nNotes load failed:", e)
        return []


def main():
    notes = load_notes_from_file("notes_stage_4.yaml")
    if notes:
        print('\n', notes)


if __name__ == "__main__":
    main()