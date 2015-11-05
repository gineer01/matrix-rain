__author__ = 'cdong'

import random
import curses
import time

def random_rain_length():
    return random.randint(curses.LINES, 3*curses.LINES//2)

def random_char():
    return chr(random.randint(0x4E00, 0x62FF))

def animate_rain(stdscr, x):
    max_length = random_rain_length()
    head = 1

    while True:
        tail = head - max_length
        if (tail < 0):
            tail = 0
        middle = head - max_length//2
        if (middle < 0):
            middle = 0

        for i in range(0, tail):
            stdscr.addstr(i, x, ' ')
        if (tail == curses.LINES):
            break

        for i in range(tail, min(middle, curses.LINES)):
            stdscr.addstr(i, x, random_char())

        for i in range(middle, min(head - 1, curses.LINES)):
            stdscr.addstr(i, x, random_char(), curses.A_REVERSE)

        if (head < curses.LINES - 1):
            stdscr.addstr(head, x, random_char())

        head = head + 1
        yield


def main(stdscr):
    # Clear screen
    curses.curs_set(0)
    stdscr.clear()

    stdscr.nodelay(True)
    rains = [animate_rain(stdscr, random.randrange(curses.COLS)) for i in range(50)]
    while True:
        for r in rains:
            try:
                next(r)
            except StopIteration:
                rains.remove(r)

        stdscr.refresh()
        time.sleep(.1)

        # ch = stdscr.getch()
        # if (ch == curses.KEY_ENTER):
        #     break
        if not rains:
            break


curses.wrapper(main)
