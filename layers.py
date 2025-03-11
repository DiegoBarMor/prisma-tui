import curses
import numpy as np

from prisma import Prisma, Align

# //////////////////////////////////////////////////////////////////////////////
class TUI(Prisma):
    def on_init(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    def on_update(self):
        shape = (curses.LINES, curses.COLS)
        bg = np.ones(shape, dtype = bool)
        fg = np.zeros(shape, dtype = bool)

        img = ~np.load("icon.npy")

        w,h = img.shape
        fg[:w, :h] = img[:curses.LINES, :curses.COLS]

        self.addlayer(bg, '.', curses.A_BOLD)
        self.addlayer(fg, '*', curses.color_pair(2))

        self.pystr("Press F1 to exit", curses.color_pair(1), Align.YBOTTOM | Align.XLEFT)
        self.pystr(f"{curses.LINES} {curses.COLS}", curses.A_REVERSE, Align.YTOP | Align.XRIGHT)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
