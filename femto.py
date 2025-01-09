# This is my tiny console text editor
# To use it on windows you should install windows-curses module
import curses


def femto(screen, initial_text=""):
    header = (
        "Edit your note text. To exit and save text press Esc",
        "To add a title surround it with {{double curly braces}}"
    )
    header_height = len(header)
    screen.clear()
    cursor_x = 0
    cursor_y = 0
    text = initial_text.split('\n') if initial_text else [""]
    # Define how many lines a page up/down moves
    page_size = curses.LINES - header_height - 1
    # Insert mode flag
    insert_mode = True
    while True:
        screen.clear()
        for i, line in enumerate(header):
            screen.addstr(i, 0, line, curses.A_REVERSE)
        for i, line in enumerate(text):
            screen.addstr(i + header_height, 0, line)
        screen.move(cursor_y + header_height, cursor_x)
        screen.refresh()
        key = screen.getch()
        match key:
            case curses.KEY_UP:
                cursor_y = max(0, cursor_y - 1)
            case curses.KEY_DOWN:
                cursor_y = min(len(text) - 1, cursor_y + 1)
            case curses.KEY_LEFT:
                cursor_x = max(0, cursor_x - 1)
            case curses.KEY_RIGHT:
                cursor_x = min(len(text[cursor_y]), cursor_x + 1)
            case curses.KEY_HOME:
                cursor_x = 0
            case curses.KEY_END:
                cursor_x = len(text[cursor_y])
            case curses.KEY_DC:  # Del key
                if cursor_x < len(text[cursor_y]):
                    text[cursor_y] = text[cursor_y][:cursor_x] + text[cursor_y][cursor_x + 1:]
                elif cursor_y < len(text) - 1:
                    text[cursor_y] += text[cursor_y + 1]
                    text.pop(cursor_y + 1)
            case curses.KEY_PPAGE:  # Page Up key
                cursor_y = max(0, cursor_y - page_size)
            case curses.KEY_NPAGE:  # Page Down key
                cursor_y = min(len(text) - 1, cursor_y + page_size)
            case 10 | 13:  # Enter key
                text.insert(cursor_y + 1, "")
                cursor_y += 1
                cursor_x = 0
            case 8 | 127:  # Backspace key
                if cursor_x > 0:
                    text[cursor_y] = text[cursor_y][:cursor_x - 1] + text[cursor_y][cursor_x:]
                    cursor_x -= 1
                elif cursor_y > 0:
                    cursor_x = len(text[cursor_y - 1])
                    text[cursor_y - 1] += text[cursor_y]
                    text.pop(cursor_y)
                    cursor_y -= 1
            case 27:  # ESC key to exit
                break
            case 9:  # Tab key
                tab_spaces = "    "  # or simply "\t" for a tab character
                text[cursor_y] = text[cursor_y][:cursor_x] + tab_spaces + text[cursor_y][cursor_x:]
                cursor_x += len(tab_spaces)
            case curses.KEY_IC:  # Insert key
                insert_mode = not insert_mode
            case _:
                if cursor_y >= len(text):
                    text.append("")
                if insert_mode or cursor_x >= len(text[cursor_y]):

                    text[cursor_y] = text[cursor_y][:cursor_x] + chr(key) + text[cursor_y][cursor_x:]
                else:
                    text[cursor_y] = text[cursor_y][:cursor_x] + chr(key) + text[cursor_y][cursor_x + 1:]
                cursor_x += 1
        # Ensure cursor is within bounds
        cursor_x = min(len(text[cursor_y]), cursor_x)
    return '\n'.join(text)