import curses
import repo_root


def log(*x, init = False):
    path_log = "log.txt"

    if init:
        with open(path_log, 'w') as file:
            file.write("")
        return

    log = f"{' '.join(map(str,x))}\n"
    with open(path_log, 'a') as file:
        file.write(log)


def main(stdscr):
    curses.curs_set(False)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    n = 5
    y = curses.LINES // 2
    x = (curses.COLS - n) // 2

    y_anim = 2
    x_anim = 3
    dy = 1
    dx = 1

    stdscr.nodelay(True)



    running = True
    while running:

        key = stdscr.getch()
        curses.flushinp()

        match key:
            case curses.KEY_F1: running = False
            case 119 | curses.KEY_UP:    y -= 1
            case 97  | curses.KEY_LEFT:  x -= 1
            case 115 | curses.KEY_DOWN:  y += 1
            case 100 | curses.KEY_RIGHT: x += 1

        curses.napms(16)

        curses.update_lines_cols()
        stdscr.erase()
        s = ((curses.COLS-n)*' ').join((n*'#' for _ in range(n)))

        ### sanitize coordinates
        y = max(0, min(y, curses.LINES - n))
        x = max(0, min(x, curses.COLS  - n))
        if (y == curses.LINES - n) and (x == curses.COLS - n): s = s[:-1]


        y_anim += dy
        x_anim += dx

        if y_anim < 0:
            y_anim = 0
            dy = -dy
        elif y_anim > curses.LINES - n:
            y_anim = curses.LINES - n
            dy = -dy

        if x_anim < 0:
            x_anim = 0
            dx = -dx
        elif x_anim > curses.COLS - n:
            x_anim = curses.COLS - n
            dx = -dx

        if (y_anim == curses.LINES - n) and (x_anim == curses.COLS - n): s = s[:-1]

        stdscr.addstr(y_anim, x_anim, s, curses.A_DIM)
        stdscr.addstr(y, x, s, curses.A_BOLD)

        stdscr.addstr(
            curses.LINES - 1, 0,
            f"Press F1 to exit {key}",
            curses.color_pair(1)
        )

        s = f"({y}, {x}) {curses.LINES} {curses.COLS}"
        stdscr.addstr(
            curses.LINES - 1, curses.COLS - len(s) - 1,
            s,curses.A_REVERSE
        )

        stdscr.refresh()



curses.wrapper(main)
