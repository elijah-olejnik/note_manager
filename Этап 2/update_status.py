from enum import Enum

class Status(Enum):
    ACTIVE = 0
    COMPLETED = 1
    TERMLESS = 2
    POSTPONED = 3

note_state = Status.TERMLESS

print(
    f"\nThe current note state is {note_state.name}\n"
    "Choose the new state:\n\n"
    "0 or active for ACTIVE\n"
    "1 or completed for COMPLETED\n"
    "3 or postponed for POSTPONED\n"
)

while True:
    user_input = input("\nSwitch state to: ").lower()
    if user_input in (note_state.name.lower(), str(note_state.value)):
        print(f"The note state remained the same: {note_state.name}")
        exit()
    match user_input:
        case '0' | 'active':
            note_state = Status.ACTIVE
        case '1' | 'completed':
            note_state = Status.COMPLETED
        case '2' | 'termless':
            note_state = Status.TERMLESS
        case '3' | 'postponed':
            note_state = Status.POSTPONED
        case _:
            print("Try again")
            continue
    break

print(f"The note state successfully changed to: {note_state.name}")