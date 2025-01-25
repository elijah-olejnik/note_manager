# This is my tiny console text editor
# To use it on windows you should install windows-curses module
import curses
from threading import Thread
import pygame
from resources import strings


def nocturne():  # Dear diary meme
    pygame.mixer.init()
    pygame.mixer.music.load("Chopin-NocturneNo1.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


def start_nocturne():  # Dear diary meme
    audio_thread = Thread(target=nocturne)
    audio_thread.start()


def stop_nocturne():  # Dear diary meme
    return pygame.mixer.music.stop()


def femto(screen, initial_text=""):
    start_nocturne()
    header = (strings.femto_str, "")
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
        key = screen.get_wch()
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
            case 10 | 13 | '\n' | '\r':  # Enter key
                text.insert(cursor_y + 1, "")
                cursor_y += 1
                cursor_x = 0
            case 8 | 127 | '\x7f' | '\x08':  # Backspace key
                if cursor_x > 0:
                    text[cursor_y] = text[cursor_y][:cursor_x - 1] + text[cursor_y][cursor_x:]
                    cursor_x -= 1
                elif cursor_y > 0:
                    cursor_x = len(text[cursor_y - 1])
                    text[cursor_y - 1] += text[cursor_y]
                    text.pop(cursor_y)
                    cursor_y -= 1
            case 27 | '\x1b':  # ESC key to exit
                break
            case 9 | '\t':  # Tab key
                tab_spaces = "    "  # or simply "\t" for a tab character
                text[cursor_y] = text[cursor_y][:cursor_x] + tab_spaces + text[cursor_y][cursor_x:]
                cursor_x += len(tab_spaces)
            case curses.KEY_IC:  # Insert key
                insert_mode = not insert_mode
            case _:
                if cursor_y >= len(text):
                    text.append("")
                if insert_mode or cursor_x >= len(text[cursor_y]):

                    text[cursor_y] = text[cursor_y][:cursor_x] + str(key) + text[cursor_y][cursor_x:]
                else:
                    text[cursor_y] = text[cursor_y][:cursor_x] + str(key) + text[cursor_y][cursor_x + 1:]
                cursor_x += 1
        # Ensure cursor is within bounds
        cursor_x = min(len(text[cursor_y]), cursor_x)
    stop_nocturne()
    return '\n'.join(text)
