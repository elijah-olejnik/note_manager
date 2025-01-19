import uuid
import yaml
from datetime import datetime
from yaml import YAMLError
from enums import NoteStatus
from custom_exceptions import FileIOError


datetime_fmt = "%d-%m-%Y %H:%M"


def str_to_deadline(str_date):
    try:
        date = datetime.strptime(str_date, datetime_fmt)
        if date <= (datetime.now()):
            raise ValueError("The deadline can be only in the future.")
        return date
    except ValueError as e:
        raise e


def generate_id():
    return uuid.uuid4()


def import_from_yaml(filename):
    try:
        with open(filename, 'r') as file:
            dicts = yaml.safe_load(file)
        if not dicts:
            raise ValueError(f"File {filename} is empty!")
        return dicts
    except (OSError, ValueError, yaml.YAMLError) as e:
        raise FileIOError(f"Import from YAML file failed: {e}")


def export_yaml(dicts, filename, rewrite = True):
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)
    def uuid_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))
    if not dicts:
        return False
    try:
        yaml.add_representer(datetime, datetime_representer)
        yaml.add_representer(NoteStatus, enum_representer)
        yaml.add_representer(uuid.UUID, uuid_representer)
        with open(filename, 'w' if rewrite else 'a') as file:
            yaml.dump(dicts, file)
        return True
    except (OSError, ValueError, YAMLError) as e:
        raise FileIOError(f"Export to YAML file failed: {e}")