import yaml
from datetime import datetime
from enum import Enum


class NoteStatus(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2
    TERMLESS = 3


class DataIntegrityError(Exception):
    pass


def load_notes_from_file(filename):
    required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            import_list = yaml.safe_load(file)
        if not import_list:
            raise ValueError(f"File {filename} is empty!")
        notes_list = []
        for dic in import_list:
            if not all(field in dic for field in required_fields):
                raise DataIntegrityError(f"Missing required fields in record: {dic}")
            try:
                note = {
                    "content": dic["content"],
                    "created_date": datetime.fromisoformat(dic["created_date"]),
                    "id_": dic["id_"],
                    "issue_date": datetime.fromisoformat(dic["issue_date"]),
                    "status": NoteStatus[dic["status"]],
                    "title": dic["title"],
                    "username": dic["username"]
                }
                notes_list.append(note)
            except (ValueError, KeyError, TypeError) as e:
                raise DataIntegrityError(f"Data format error in record {dic}: {e}")
        return notes_list
    except (OSError, ValueError, yaml.YAMLError, DataIntegrityError) as e:
        print("\nNotes load failed:", e)
        return []


def main():
    notes = load_notes_from_file("notes_stage_4.yaml")
    if notes:
        print('\n', notes)


if __name__ == "__main__":
    main()