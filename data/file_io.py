from utils import FileIOError, NoteStatus
from json import JSONDecodeError
from datetime import datetime
from enum import Enum
from uuid import UUID
import yaml
import json
from resources import strings


def import_from_yaml(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            dicts = yaml.safe_load(file)
        if not dicts:
            raise FileIOError(strings.file_str + str(filename) + strings.is_empty_str)
        return dicts
    except (OSError, ValueError, yaml.YAMLError) as e:
        raise FileIOError(strings.yaml_import_failed_str + str(e))


def export_to_yaml(dicts, filename, rewrite=True):
    def datetime_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.isoformat())
    def enum_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", data.name)
    def uuid_representer(dumper, data):
        return dumper.represent_scalar("tag:yaml.org,2002:str", str(data))
    if not dicts:
        raise ValueError(strings.empty_list_export_str)
    try:
        yaml.add_representer(datetime, datetime_representer)
        yaml.add_representer(NoteStatus, enum_representer)
        yaml.add_representer(UUID, uuid_representer)
        with open(filename, 'w' if rewrite else 'a', encoding='utf-8') as file:
            yaml.dump(dicts, file, allow_unicode=True)
    except (OSError, ValueError, yaml.YAMLError) as e:
        raise FileIOError(strings.yaml_export_failed_str + str(e))


def import_from_json(filename):
    try:
        with open(filename) as file:
            dicts = json.load(file)
        if not dicts:
            raise FileIOError(strings.file_str + str(filename) + strings.is_empty_str)
        return dicts
    except (OSError, JSONDecodeError) as e:
        raise FileIOError(strings.json_import_failed_str + str(e))


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
        raise ValueError(strings.empty_list_export_str)
    try:
        with open(filename, 'w' if rewrite else 'a', encoding='utf-8') as file:
            json.dump(dicts, file, cls=NoteEncoder, indent=4, ensure_ascii=False) # type: ignore
    except (ValueError, OSError) as e:
        raise FileIOError(strings.json_export_failed_str + str(e))
