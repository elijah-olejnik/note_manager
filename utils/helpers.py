import yaml
from datetime import datetime
from dataclasses import asdict
from yaml import YAMLError
from enums import NoteStatus
from custom_exceptions import DataIntegrityError, FileIOError


datetime_fmt = "%d-%m-%Y %H:%M"


def str_to_deadline(str_date):
    try:
        date = datetime.strptime(str_date, datetime_fmt)
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date
    except ValueError as e:
        raise e


def import_yaml(filename):
    required_fields = ("content", "created_date", "id_", "issue_date", "status", "title", "username")
    try:
        with open(filename, 'r') as file:
            import_list = yaml.safe_load(file)
        if not import_list:
            raise ValueError(f"File {filename} is empty!")
        notes_list = []
        for d in import_list:
            if not all(field in d for field in required_fields):
                raise DataIntegrityError(f"Missing required fields in record: {d}")
            try:
                note = Note(
                    content=d["content"],
                    created_date=datetime.fromisoformat(d["created_date"]),
                    id_=d["id_"],
                    issue_date=datetime.fromisoformat(d["issue_date"]),
                    status=NoteStatus[d["status"]],
                    title=d["title"],
                    username=d["username"]
                )
                notes_list.append(note)
            except(ValueError, KeyError, TypeError) as e:
                raise DataIntegrityError(f"Data format error in record {d}: {e}. Check file content.")
        return notes_list
    except (OSError, ValueError, yaml.YAMLError, DataIntegrityError) as e:
        raise FileIOError(f"Import from YAML file failed: {e}")


def export_yaml(notes, filename, rewrite = True):
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)
    if not notes:
        return False
    export_list = [asdict(note) for note in notes]
    try:
        yaml.add_representer(datetime, datetime_representer)
        yaml.add_representer(NoteStatus, enum_representer)
        with open(filename, 'w' if rewrite else 'a') as file:
            yaml.dump(export_list, file)
        return True
    except (OSError, ValueError, YAMLError) as e:
        raise FileIOError(f"Export to YAML file failed: {e}")