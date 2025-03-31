import json
import curses

def main(stdscr: curses.window):
    path_palette = "tests/palette.pal"
    with open(path_palette, 'r') as file:
        palette = json.load(file)

    # palette should be of 248 colors max, the first 8 are to be reserved to the default curses values

    # n = 256
    # c = 1000 // n
    char = -1
    while char != curses.KEY_F1:
        _,w = stdscr.getmaxyx()
        stdscr.erase()
        for i,color in enumerate(palette):
            y, x = divmod(i*4, w)

            if i >= 8:
                curses.init_color(i, *color)
            # curses.init_color(i, 0, 0, i*c)

            if i:
                curses.init_pair(i, curses.COLOR_BLACK, i)

            # stdscr.addstr(y, x, f"{i:03}")
            stdscr.addstr(y, x, f"{i:03}", curses.color_pair(i))

        char = stdscr.getch()

curses.wrapper(main)
