__author__ = 'cdong'

import random
import curses
import time

#Sleep between frame after refresh so that user can see the frame. Value 0.01 or lower results in flickering because the
# animation is too fast.
SLEEP_BETWEEN_FRAME = .04

#How fast the rain should fall
FALLING_SPEED = 1

#The max number of falling rains
MAX_RAIN_COUNT = 10


def get_matrix_code_chars():
    l = [chr(i) for i in range(0x21, 0x7E)]
    # half-width katakana. See https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms
    l.extend([chr(i) for i in range(0xFF66, 0xFF9D)])
    return l

MATRIX_CODE_CHARS = get_matrix_code_chars()

def random_char():
    return random.choice(MATRIX_CODE_CHARS)

def random_rain_length():
    return random.randint(curses.LINES//2, 3*curses.LINES//2)

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

        if (tail >= curses.LINES):
            break

        for i in range(tail, min(middle, curses.LINES)):
            stdscr.addstr(i, x, random_char(), curses.color_pair(1))

        for i in range(middle, min(head, curses.LINES)):
            stdscr.addstr(i, x, random_char(), curses.color_pair(1) | curses.A_BOLD)

        if (head < curses.LINES - 1):
            stdscr.addstr(head, x, random_char(), curses.color_pair(0) | curses.A_STANDOUT | curses.A_BLINK)

        head = head + FALLING_SPEED
        yield


def main(stdscr):
    stdscr.addstr(0, 0, "Press any key to start. Press any key (except SPACE) to stop.")
    ch = stdscr.getch() #Wait for user to press something before starting
    config(stdscr)

    rains = []

    while True:
        add_rain(rains, stdscr)

        stdscr.clear()
        for r in rains:
            try:
                next(r)
            except StopIteration:
                rains.remove(r)

        # getch() already includes refresh()
        # stdscr.refresh()
        # debugging info
        # stdscr.addstr(0, 0, "Key pressed: {}".format(ch))

        ch = stdscr.getch()
        if ch != curses.ERR and ch != ord(' '): #Use space to proceed animation if nodelay is False
            break

        time.sleep(SLEEP_BETWEEN_FRAME)


def config(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    global MAX_RAIN_COUNT
    MAX_RAIN_COUNT = curses.COLS//3


def add_rain(rains, stdscr):
    if len(rains) < MAX_RAIN_COUNT:
        rains.append(animate_rain(stdscr, random.randrange(curses.COLS - 1)))


curses.wrapper(main)
