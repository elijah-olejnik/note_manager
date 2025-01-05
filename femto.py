# This script is the tiniest tui text editor I've called femto
import curses

# Just in one function
def femto(stdscr, initial_text = ""):
    stdscr.clear()
    cursor_x = 0
    cursor_y = 0
    text = initial_text.split('\n') if initial_text else [""]
    while True:
        stdscr.clear()
        for i, line in enumerate(text):
            stdscr.addstr(i, 0, line)
        stdscr.move(cursor_y, cursor_x)
        stdscr.refresh()
        key = stdscr.getch()
        match key:
            case curses.KEY_UP:
                cursor_y = max(0, cursor_y - 1)
            case curses.KEY_DOWN:
                cursor_y = min(len(text) - 1, cursor_y + 1)
            case curses.KEY_LEFT:
                cursor_x = max(0, cursor_x - 1)
            case curses.KEY_RIGHT:
                cursor_x = min(len(text[cursor_y]), cursor_x + 1)
            case 10 | 13:  # Enter key
                text.insert(cursor_y + 1, "")
                cursor_y += 1
                cursor_x = 0
            case 127:  # Backspace key
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
            case _:
                if cursor_y >= len(text):
                    text.append("")
                text[cursor_y] = text[cursor_y][:cursor_x] + chr(key) + text[cursor_y][cursor_x:]
                cursor_x += 1
        # Ensure cursor is within bounds
        cursor_x = min(len(text[cursor_y]), cursor_x)
    return '\n'.join(text)