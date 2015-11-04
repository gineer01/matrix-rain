__author__ = 'cdong'

import random
import curses
import time

def random_rain_length():
    return random.randint(curses.LINES/2, curses.LINES)

def random_char():
    return chr(random.randint(0x4E00, 0x62FF))

def animate_rain(stdscr, x, y):
    length = random_rain_length()
    stdscr.addstr(y, x, "{} {} {}".format(x, y, length))

    done = False
    while not done:
        for i in range(y, length):
            stdscr.addstr(i, x, random_char(), curses.A_REVERSE)
        yield


def main(stdscr):
    # Clear screen
    stdscr.clear()

    stdscr.nodelay(True)
    rains = [animate_rain(stdscr, random.randrange(curses.COLS - 10), random.randrange(curses.LINES/2)) for i in range(50)]
    while True:
        for r in rains:
            next(r)

        time.sleep(.01)
        ch = stdscr.getch()
        if (ch == curses.KEY_ENTER):
            break


curses.wrapper(main)
