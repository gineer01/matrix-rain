#!/usr/bin/env python3

import curses
import matrix

line = 0
def display_info(stdscr):
    display_info_line(stdscr, "COLS: {}".format(curses.COLS))
    display_info_line(stdscr, "LINES: {}".format(curses.LINES))
    display_info_line(stdscr, "Bold", curses.color_pair(0) | curses.A_BOLD)
    display_info_line(stdscr, "Blink", curses.A_BLINK)
    display_info_line(stdscr, "Blink + Standout", curses.A_BLINK | curses.A_STANDOUT)
    display_info_line(stdscr, "Stand out", curses.A_STANDOUT)
    display_info_line(stdscr, "Dim", curses.A_DIM)
    display_info_line(stdscr, "Underline", curses.A_UNDERLINE)
    display_info_line(stdscr, "Normal", curses.A_NORMAL)
    display_info_line(stdscr, "Reverse", curses.A_REVERSE)
    display_info_line(stdscr, "Color", curses.A_COLOR)
    display_info_line(stdscr, "Chartext", curses.A_CHARTEXT)
    display_info_line(stdscr, "Low", curses.A_LOW)
    display_info_line(stdscr, "Left", curses.A_LEFT)
    display_info_line(stdscr, "Can change color pair: %s" % curses.can_change_color())
    display_info_line(stdscr, "Color pairs: %s" % curses.COLOR_PAIRS)
    display_info_line(stdscr, "# of colors: %d" % curses.COLORS)

    if curses.can_change_color():
        display_info_line(stdscr, "The terminal should show a green gradient below. If it's colorful instead, curses can't change terminal color.")
        matrix.init_colors()
        for i in range(matrix.NUMBER_OF_COLOR + 1):
            color_num = matrix.START_COLOR_NUM + i
            display_info_line(stdscr, "Pair {} {} {}".format(color_num, curses.color_content(color_num), curses.pair_content(color_num)), curses.color_pair(color_num))

    stdscr.getch()



def display_info_line(stdscr, info, attr=curses.A_NORMAL):
    global line
    stdscr.addstr(line, 0, info, attr)
    line = line + 1
    if line == curses.LINES:
        stdscr.getch()
        line = 0

curses.wrapper(display_info)