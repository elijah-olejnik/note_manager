from curses import wrapper
from datetime import datetime
from .enums import NoteStatus, InputType
from resources import strings
from .femto import femto


def get_value_from_console(input_type, prompt="", enum_=None):
    """The function handles and checks the correctness of the user input from terminal
    depending on the given InputType value. The argument 'prompt' is used for the input()
    function, the argument 'enum_' used only if the InputType is InputType.ENUM_VAL.
    Raises a KeyError and ValueError exceptions if input is incorrect.
    """
    while True:
        try:
            user_input = input(prompt).strip() if input_type != InputType.TEXT else wrapper(femto, prompt)
            if not user_input and input_type != InputType.DATE:
                continue
            match input_type:
                case InputType.INT:
                    return int(user_input)
                case InputType.ENUM_VAL:
                    return input_to_enum_value(user_input, enum_)
                case InputType.DATE:
                    return str_to_date(user_input)
                case _:
                    return user_input
        except (KeyError, ValueError) as e:
            print('\n', e, '\n')


def str_to_date(str_date, is_deadline=True):
    """The function converts user input string to a datetime
    object. If is_deadline=True the function compare the entered model
    with datetime.now() to assure that deadline is in the future.
    Raises ValueError if input doesn't fit date format or the deadline condition.
    """
    try:
        date = datetime.strptime(str_date, "%d-%m-%Y %H:%M")
        if is_deadline and date <= (datetime.now()):
            raise ValueError(strings.deadline_invalid_str)
        return date
    except ValueError as e:
        raise e


def date_to_str(date, is_deadline, state=NoteStatus.TERMLESS):
    """The function convert the datetime object to string or return
    NO DEADLINE if note status is TERMLESS or COMPLETED. If deadline
    parameter is False, the function just convert datetime to string.
    """
    if not is_deadline or state not in (NoteStatus.TERMLESS, NoteStatus.COMPLETED):
        return datetime.strftime(date, "%B %d, %Y %H:%M")
    else:
        return strings.no_deadline_str


def input_to_enum_value(input_str, enum_class):
    """The function convert the user input to an enum value or value name
    of a given Enum in the second argument. Raises the ValueError if
    the given model doesn't match with any of Enum values or names.
    """
    try:
        if not input_str.isdigit():
            name = input_str.upper()
            return enum_class[name]
        else:
            value = int(input_str) - 1
            return enum_class(value)
    except (KeyError, ValueError) as e:
        raise ValueError(strings.enum_error_str + str(e))
