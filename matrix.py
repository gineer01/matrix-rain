#!/usr/bin/env python3

import random
import curses
import time

# Sleep between frame after refresh so that user can see the frame. Value 0.01 or lower results in flickering because
# the animation is too fast.
SLEEP_BETWEEN_FRAME = .04  # about 25 frames/s is good enough

# How fast the rain should fall. In config, we change it according to screen.
FALLING_SPEED = 2

# The max number of falling rains. In config, we change it according to screen.
MAX_RAIN_COUNT = 10

# Color gradient for rain
COLOR_STEP = 20
NUMBER_OF_COLOR = 45  # The darkest color is 1000 - COLOR_STEP * NUMBER_OF_COLOR. This should be >= 0
USE_GRADIENT = False
START_COLOR_NUM = 128  # The starting number for color in gradient to avoid changing the first 16 basic colors

# Different styles for rain head
HEAD_STANDOUT = curses.COLOR_WHITE | curses.A_STANDOUT  # look better for small font
HEAD_BOLD = curses.COLOR_WHITE | curses.A_BOLD  # look better for larger font

# TODO This can be a namedtuple
options = {
    'head': HEAD_BOLD,
    'speed': FALLING_SPEED,
    'count': MAX_RAIN_COUNT,
    'opening_title': " ".join("The Matrix".upper()),
    'end_title': " ".join("The Matrix. Goodbye!".upper()),
}


# Reset the options value according to screen size
def config(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)

    init_colors()

    options['count'] = MAX_COLS // 2
    options['speed'] = 1 + curses.LINES // 25


def init_colors():
    curses.start_color()
    global USE_GRADIENT
    USE_GRADIENT = curses.can_change_color()  # use xterm-256 if this is false

    if USE_GRADIENT:
        curses.init_color(curses.COLOR_WHITE, 1000, 1000, 1000)
        curses.init_color(curses.COLOR_BLACK, 0, 0, 0)  # make sure background is black
        for i in range(NUMBER_OF_COLOR + 1):
            green_value = (1000 - COLOR_STEP * NUMBER_OF_COLOR) + COLOR_STEP * i
            curses.init_color(START_COLOR_NUM + i, 0, green_value, 0)
            curses.init_pair(START_COLOR_NUM + i, START_COLOR_NUM + i, curses.COLOR_BLACK)
    else:
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)


def get_matrix_code_chars():
    l = [chr(i) for i in range(0x21, 0x7E)]
    # half-width katakana. See https://en.wikipedia.org/wiki/Halfwidth_and_fullwidth_forms
    l.extend([chr(i) for i in range(0xFF66, 0xFF9D)])
    return l


MATRIX_CODE_CHARS = get_matrix_code_chars()


def random_char():
    return random.choice(MATRIX_CODE_CHARS)


def random_rain_length():
    return random.randint(curses.LINES // 2, curses.LINES)


def rain_forever(stdscr, pool):
    """
    Make rain forever by choosing a random column from pool and make rain at that column and repeat

    :param stdscr: curses's screen object
    :param pool: a list of int: a list of available columns to choose randomly from
    :return: None
    """
    while True:
        if pool:
            x = random.choice(pool)
            pool.remove(x)
        else:
            break

        # We want most of the rain start from 0, but some starts randomly
        begin = random.randint(-curses.LINES // 2, curses.LINES // 3)
        if begin < 0:
            begin = 0

        # We want most of the rain end at the bottom but some randomly end before reaching the bottom
        end = random.randint(curses.LINES // 2, 2 * curses.LINES)
        if end > curses.LINES:
            end = curses.LINES

        should_stop = yield from rain_once(stdscr, x, begin, end)

        if should_stop:
            break
        else:
            pool.append(x)


def rain_once(stdscr, x, begin, end, last_char=None):
    """
    Make rain once at column x from line begin to line end

    :param stdscr: curses's screen object
    :param x: the column of this rain on the screen
    :param begin: the line to begin
    :param end: the line to end
    :param last_char: the last character to show
    :return: the value received from yield
    """
    max_length = random_rain_length()
    speed = random.randint(1, options['speed'])
    r = yield from animate_rain(stdscr, x, begin, end, max_length, speed, last_char)
    return r


def animate_rain(stdscr, x, begin, end, max_length, speed=FALLING_SPEED, last_char=None):
    """
    A rain consists of 3 parts: head, body, and tail
    Head: the white leading rain drop
    Body: the fading trail
    Tail: empty space behind the rain trail

    :param stdscr: curses's screen object
    :param x: the column of this rain on the screen
    :param begin: the line to begin
    :param end: the line to end
    :param max_length: the length of this rain
    :param speed: how fast a rain should fall (the number of lines it jumps each animation frame)
    :param last_char: the last character to show
    :return: the value received from yield
    """
    head, tail = begin, begin

    head_style = options['head']

    def show_head():
        if head < end:
            stdscr.addstr(head, x, random_char(), head_style)

    def get_color(i):
        color_num = NUMBER_OF_COLOR - (head - i) + 1
        if color_num < 0:
            color_num = 0
        return curses.color_pair(START_COLOR_NUM + color_num)

    def show_body():
        if USE_GRADIENT:
            for i in range(tail, min(head, end)):
                stdscr.addstr(i, x, random_char(), get_color(i))
        else:
            middle = head - max_length // 2
            if (middle < begin):
                middle = begin
            for i in range(tail, min(middle, end)):
                stdscr.addstr(i, x, random_char(), curses.color_pair(1))
            for i in range(middle, min(head, end)):
                stdscr.addstr(i, x, random_char(), curses.color_pair(1) | curses.A_BOLD)

    def show_tail():
        for i in range(max(begin, tail - speed), min(tail, end)):
            stdscr.addstr(i, x, ' ', curses.color_pair(0))

    while tail < end:
        tail = head - max_length
        if tail < begin:
            tail = begin
        else:
            show_tail()

        show_body()

        show_head()

        head = head + speed
        r = yield

    if last_char:
        stdscr.addstr(end - 1, x, last_char, curses.color_pair(0))

    return r


def update_style():
    """
    Cycle thru different styles
    :return: None
    """
    options['head'] = HEAD_BOLD if options['head'] == HEAD_STANDOUT else HEAD_STANDOUT


def show_title(stdscr, y, x, title):
    """
    Show the title similar to the movie title in The Matrix movie
    The title looks best if it's upper case and with space between letters. Example:
        show_title(stdscr, x, y, " ".join("Hello world!".upper()))

    :param stdscr: curses's screen object
    :param y: the line to show the title
    :param x: the column to show the title
    :param title: the string to show
    :return: None
    """
    pool = list(range(MAX_COLS))
    rains = []
    count = 0

    for i, s in enumerate(title):  # for each visible letter, add a rain drop
        col = x + i
        if col >= MAX_COLS:
            break
        pool.remove(col)
        if s != ' ':  # space is not visible
            rains.append(rain_once(stdscr, col, 0, y, s))
            count = count + 1

    for i in range(len(pool) // 3):
        rains.append(rain_forever(stdscr, pool))

    stdscr.clear()
    should_stop = None
    while True:
        for r in rains:
            try:
                r.send(should_stop)
            except StopIteration:
                rains.remove(r)
                count = count - 1

        if count == 0:  # finish the title, wait for others to finish then exit
            should_stop = True

        ch = stdscr.getch()
        if ch != curses.ERR and ch != ord(' '):  # Use space to proceed animation if nodelay is False
            break  # exit

        if not rains:  # all the rains have stopped
            break

        time.sleep(SLEEP_BETWEEN_FRAME)


def main(stdscr):
    # Do not use the last column due to curses limit
    # See https://docs.python.org/3/library/curses.html#curses.window.addstr
    #   Attempting to write to the lower right corner will cause an exception to be raised
    global MAX_COLS
    MAX_COLS = curses.COLS - 1

    stdscr.addstr(0, 0, "Press any key to start. Press any key (except SPACE) to stop.")
    stdscr.addstr(1, 0, "Press key 'h' to try a different style.")
    stdscr.addstr(curses.LINES // 3, MAX_COLS // 4, options["opening_title"])
    ch = stdscr.getch()  # Wait for user to press something before starting
    config(stdscr)

    rains = []
    pool = list(range(MAX_COLS))

    while True:
        add_rain(rains, stdscr, pool)

        for r in rains:
            next(r)

        ch = stdscr.getch()
        if ch != curses.ERR and ch != ord(' '):  # Use space to proceed animation if nodelay is False
            if ch == ord('h'):
                update_style()
            else:
                show_title(stdscr, curses.LINES // 2, MAX_COLS // 3, options["end_title"])
                break  # exit

        time.sleep(SLEEP_BETWEEN_FRAME)


def add_rain(rains, stdscr, pool):
    if (len(rains) < options['count']) and (len(pool) > 0):
        rains.append(rain_forever(stdscr, pool))


if __name__ == "__main__":
    curses.wrapper(main)
