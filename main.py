from interface import NoteManagerCLI
import gettext
import sys


def main():
    gettext.bindtextdomain('note_manager', 'locales')
    gettext.textdomain('note_manager')
    if sys.stdout.isatty():
        interface = NoteManagerCLI()
        interface.run()
    return 0


if __name__ == "__main__":
    main()