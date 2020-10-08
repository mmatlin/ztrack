from appdirs import user_data_dir
from configparser import ConfigParser
from pathlib import Path
import yaml
from itertools import chain
from .default_settings import default_settings

RECORD_TYPE_ITEM = "item"
RECORD_TYPE_GROUP = "group"

_APP_INFO_FILENAME = "app_info.ini"


def _get_cwd():
    return Path(__file__).parent


def _get_appdata_location():
    config = ConfigParser()
    config.read(_get_cwd() / _APP_INFO_FILENAME)
    app_name, app_author = config["info"]["app_name"], config["info"]["app_author"]
    return Path(user_data_dir(appname=app_name, appauthor=app_author, roaming=True))


# TODO: make data directory changeable by user
_APPDATA = _get_appdata_location()  # This should not change on any one machine

_SETTINGS_FILENAME = "settings.ini"
_LABELS_FILENAME = "labels.yaml"
_RECORDS_FILENAME = "records.yaml"
_STATE_FILENAME = "state.yaml"


_LABELS_PATH = _APPDATA / _LABELS_FILENAME
_RECORDS_PATH = _APPDATA / _RECORDS_FILENAME
_STATE_PATH = _APPDATA / _STATE_FILENAME

_SETTINGS_PATH = _APPDATA / _SETTINGS_FILENAME


def first_run():
    _APPDATA.mkdir(parents=True, exist_ok=True)

    yaml_paths = (_LABELS_PATH, _RECORDS_PATH, _STATE_PATH)
    ini_paths = (_SETTINGS_PATH,)

    for path in chain(yaml_paths, ini_paths):
        try:
            path.touch(exist_ok=False)
            if path in yaml_paths:
                with open(path, "w") as path_stream:
                    yaml.dump(dict(), path_stream)
        except FileExistsError:
            print(f"{path} already exists, skipping creation")
    _initialize_settings()
    _initialize_state()


def _initialize_settings():
    with open(_SETTINGS_PATH, "w") as settings_stream:
        config = ConfigParser()
        config.read_dict(default_settings)
        config.write(settings_stream)


def _initialize_state():
    _set_state(
        {
            "default_label_info": {"label": "", "record_type": ""},
            "label_info": {"label": "", "record_type": ""},
            "activity_notes": "",
            "toggle": {"toggled": False},
        }
    )


def get_settings():
    config = ConfigParser()
    config.read(_SETTINGS_PATH)
    return config


def get_state():
    with open(_STATE_PATH) as state_stream:
        return yaml.safe_load(state_stream)


def _set_state(state):
    with open(_STATE_PATH, "w") as state_stream:
        yaml.safe_dump(state, state_stream)


def set_default_label_info(label, record_type):
    state = get_state()
    state["default_label_info"] = {"default_label": label, "record_type": record_type}
    _set_state(state)


def set_label_info(label, *args):
    state = get_state()
    labels = get_labels()
    record_type = labels[label]["record_type"]
    state["label_info"] = {"label": label, "record_type": record_type}
    _set_state(state)
    new_end_label_data = labels.pop(label)
    labels[label] = new_end_label_data
    _set_labels(labels)


def _get_label_info():
    state = get_state()
    return state["label_info"]


def set_activity_notes(notes):
    state = get_state()
    state["activity_notes"] = notes
    _set_state(state)


def _get_activity_notes():
    state = get_state()
    return state["activity_notes"]


def toggle_on(start):
    state = get_state()
    state["toggle"] = {
        "toggled": True,
        "start": start,
    }
    _set_state(state)


def toggle_off(end):
    state = get_state()
    label_info = _get_label_info()
    add_record(
        state["toggle"]["start"],
        end,
        label_info["label"],
        label_info["record_type"],
        _get_activity_notes(),
    )
    state["toggle"] = {"toggled": False}
    _set_state(state)


def get_labels():
    with open(_LABELS_PATH) as labels_stream:
        return yaml.safe_load(labels_stream)


def _get_groups(labels=None):
    # Labels is not set to get_labels() by default in the function declaration
    # so that get_labels is not called on import of data_interface
    if labels is None:
        labels = get_labels()
    return {
        label: data
        for label, data in labels.items()
        if data["record_type"] == RECORD_TYPE_GROUP
    }


def _get_items():
    return {
        label: data
        for label, data in get_labels().items()
        if data["record_type"] == RECORD_TYPE_ITEM
    }


def _set_labels(labels):
    with open(_LABELS_PATH, "w") as labels_stream:
        yaml.safe_dump(labels, labels_stream, sort_keys=False)


def add_group(label, items):
    labels = get_labels()
    groups = _get_groups(labels)
    if label not in groups:
        labels[label] = {label: {"record_type": RECORD_TYPE_GROUP, "items": items}}
    _set_labels(labels)


def _get_records():
    with open(_RECORDS_PATH) as records_stream:
        return yaml.safe_load(records_stream)


def _set_records(records):
    with open(_RECORDS_PATH, "w") as records_stream:
        yaml.safe_dump(records, records_stream, sort_keys=False)


def add_record(start, end, label, record_type, notes):
    write_dict = {
        "record_type": record_type,
        "data": {
            "end": end,
            "duration": (end - start).total_seconds(),
            "label": label,
            "notes": notes,
        },
    }
    if record_type == RECORD_TYPE_GROUP:
        write_dict["data"]["items"] = _get_groups()[label]
    records = _get_records()
    if start not in records:
        records[start] = write_dict
    _set_records(records)
