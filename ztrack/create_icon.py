from pystray import Icon as icon, Menu as menu, MenuItem as menu_item
from PIL import Image, ImageDraw
import pathlib
from datetime import datetime as dt
from functools import partial
from .data_interface import (
    get_settings,
    get_state,
    get_labels,
    set_label_info,
    toggle_on,
    toggle_off,
)


def create_icon():  # TODO: bring things out of this function
    off_logo_path = pathlib.Path(__file__).parent / "assets/off_logo.png"
    on_logo_path = pathlib.Path(__file__).parent / "assets/on_logo.png"
    off_logo = Image.open(off_logo_path)
    on_logo = Image.open(on_logo_path)

    if (toggle_state := get_state()["toggle"]["toggled"]) is True:
        initial_logo = on_logo
    elif toggle_state is not True:
        initial_logo = off_logo

    def toggle_clock(ztrack_pystray_icon, *pystray_args):
        if (toggle_state := get_state()["toggle"]["toggled"]) is True:
            toggle_off(dt.now())
            ztrack_pystray_icon.icon = off_logo
        elif toggle_state is not True:
            toggle_on(dt.now())
            ztrack_pystray_icon.icon = on_logo

    def toggle_text(*pystray_args):
        return f"Toggle {'off' if get_state()['toggle']['toggled'] else 'on'}"

    def selected_label_text(*pystray_args):
        return f"Selected: {get_state()['label_info']['label']}"

    def create_select_activity_submenu():
        activity_submenu_length = get_settings()["select_label_submenu_length"][
            "length"
        ]
        labels = reversed(get_labels())
        current_label = get_state()["label_info"]["label"]
        count = 0
        for label in labels:
            if count == activity_submenu_length:
                return
            if label == current_label:
                continue
            count += 1
            yield menu_item(label, partial(set_label_info, label))

    def select_default_label():
        set_label_info(get_state()["default_label_info"]["label"])

    def select_default_text(*pystray_args):
        return f"Select default: {get_state()['default_label_info']['label']}"

    def select_default_enabled(*pystray_args):
        state = get_state()
        return (
            state["label_info"]["label"] != get_state()["default_label_info"]["label"]
        )

    def settings():
        pass

    def stop_icon(ztrack_pystray_icon, *pystray_args):
        ztrack_pystray_icon.stop()

    ztrack_icon = icon("ztrack", icon=initial_logo, title="ztrack")

    main_menu = menu(
        menu_item(toggle_text, partial(toggle_clock, ztrack_icon), default=True),
        menu.SEPARATOR,
        menu_item(selected_label_text, lambda: None, enabled=False),
        menu_item(
            select_default_text, select_default_label, enabled=select_default_enabled
        ),
        menu_item("Select activity...", menu(create_select_activity_submenu)),
        menu_item("Save group", lambda: None, enabled=False),  # TODO: implement groups
        menu.SEPARATOR,
        menu_item("Settings", settings),  # TODO: add a GUI for editing settings
        menu_item("Exit ztrack", partial(stop_icon, ztrack_icon)),
    )
    ztrack_icon.menu = main_menu

    ztrack_icon.run()
