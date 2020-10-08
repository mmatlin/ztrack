default_settings = {
    "select_label_submenu_length": {
        "length": 5,
        "text": 'Maximum "select activity" submenu length',
        "type": int,  # TODO: use a different means of specifying field type
    },
    "change_label_commits_record": {  # TODO: implement this setting
        "state": False,
        "text": "Changing activity while toggled on stops and records the current activity, then starts a new one",
        "type": bool,
    },
}
