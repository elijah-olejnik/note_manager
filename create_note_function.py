from datetime import datetime, timedelta
from enum import Enum
from typing import Tuple, Union
import curses
import femto


class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    POSTPONED = 2


date_fmts = ("%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y")


def is_date_acceptable(str_date="") -> Tuple[bool, Union[datetime, ValueError]]:
    for fmt in date_fmts:
        try:
            date = datetime.strptime(str_date, fmt)
            if date < datetime.now():
                raise ValueError("The deadline can be only in the future. Try Again.")
            return True, date
        except ValueError:
            continue
    return False, ValueError(f"The date should be in\n{'\n'.join(fmt for fmt in date_fmts)}")


def create_note():
    note = {
        "username" : ["", "Enter your name: "],
        "title" : ["", "Enter the note title: "],
        "content" : "",
        "status" : [
            Status.ACTIVE,
            "Enter the note state\n"
            "'0' for ACTIVE\n"
            "'1' for COMPLETED\n"
            "'2' for POSTPONED\n"
            "Status: "
        ],
        "created_date" : datetime.now(),
        "issue_date" : [
            datetime.now() + timedelta(weeks=1),
            "Enter the deadline date in appropriate format\n"
            f"{'\n'.join(fmt for fmt in date_fmts)}\n"
            "or press Enter to leave the default value (1 week): "
        ]
    }
    for key, value in note.items():
        if key == "created_date":
            continue
        while True:
            user_input = input(value[1]) if key != "content" else curses.wrapper(femto.femto)
            if key == "status":
                if user_input not in ('0', '1', '2'):
                    print("\nIncorrect input. Try again.\n")
                    continue
                note[key] = Status(int(user_input))
            elif key == "issue_date":
                result = value[0]
                if not user_input:
                    note[key] = result
                    break
                result = is_date_acceptable(user_input)
                if not result[0]:
                    print("\n", result[1], "\n")
                    continue
                note[key] = result[1]
            else:
                if not user_input:
                    continue
                note[key] = user_input
            break
    return note


def main():
    while True:
        command = input("\nCreate note? (y|n): ")
        if command == 'y':
            result = create_note()
            print("\nNote created:", result)
        elif command == 'n':
            print("\nQuitting...")
        else:
            continue
        break
    return 0


if __name__ == "__main__":
    main()