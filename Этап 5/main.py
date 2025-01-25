from interface import NoteManagerCLI
import sys


def main():
    if sys.stdout.isatty():
        interface = NoteManagerCLI()
        interface.run()
    return 0


if __name__ == "__main__":
    main()
