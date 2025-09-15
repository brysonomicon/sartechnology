from constants.application import Application


def main():
    app = Application()
    app.protocol("WM_DELETE_WINDOW", app.on_close)  # Ensure clean exit
    app.mainloop()


if __name__ == "__main__":
    main()
