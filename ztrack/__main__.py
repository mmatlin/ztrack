def run():
    from .data_interface import first_run, get_state
    from .create_icon import create_icon

    try:
        get_state()
    except:
        first_run()
    create_icon()


if __name__ == "__main__":
    # __name__ == "__main__" is true if ztrack is called with python -m ztrack, otherwise __name__ == "ztrack.__main__"
    run()
