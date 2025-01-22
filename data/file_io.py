from utils import FileIOError, NoteStatus
from json import JSONDecodeError
from datetime import datetime
from enum import Enum
from uuid import UUID
import yaml
import json
import gettext

_ = gettext.gettext


def import_from_yaml(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            dicts = yaml.safe_load(file)
        if not dicts:
            raise FileIOError(_("File ") + str(filename) + _(" is empty!"))
        return dicts
    except (OSError, ValueError, yaml.YAMLError) as e:
        raise FileIOError(_("Import from YAML file failed: ") + str(e))


def export_to_yaml(dicts, filename, rewrite=True):
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)
    def uuid_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))
    if not dicts:
        raise ValueError(_("You're trying to export an empty list."))
    try:
        yaml.add_representer(datetime, datetime_representer)
        yaml.add_representer(NoteStatus, enum_representer)
        yaml.add_representer(UUID, uuid_representer)
        with open(filename, 'w' if rewrite else 'a', encoding='utf-8') as file:
            yaml.dump(dicts, file, allow_unicode=True)
    except (OSError, ValueError, yaml.YAMLError) as e:
        raise FileIOError(_("Export to YAML file failed: ") + str(e))


def import_from_json(filename):
    try:
        with open(filename) as file:
            dicts = json.load(file)
        if not dicts:
            raise FileIOError(_("File ") + str(filename) + str(" is empty!"))
        return dicts
    except (OSError, JSONDecodeError) as e:
        raise FileIOError(_("Import from JSON file failed: ") + str(e))


def export_to_json(dicts, filename, rewrite=True):
    class NoteEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Enum):
                return obj.name
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif isinstance(obj, UUID):
                return str(obj)
            else:
                return obj
    if not dicts:
        raise ValueError(_("You're trying to export an empty list."))
    try:
        with open(filename, 'w' if rewrite else 'a', encoding='utf-8') as file:
            json.dump(dicts, file, cls=NoteEncoder, indent=4, ensure_ascii=False) # type: ignore
    except (ValueError, OSError) as e:
        raise FileIOError(_("Export to JSON file failed: ") + str(e))