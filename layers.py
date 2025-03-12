import curses
import numpy as np

from prisma import Prisma, Layer

# //////////////////////////////////////////////////////////////////////////////
class TUI(Prisma):
    def on_init(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

    def on_update(self):
        shape = (curses.LINES, curses.COLS)
        bg = Layer()
        bg.addchattr('.', curses.A_BOLD)
        bg.arr = ~bg.arr

        fg = Layer.init_from_img("icon.npy")
        fg.addchattr('*', curses.color_pair(2))

        self.addlayer(bg)
        self.addlayer(fg)

        self.pystr("Press F1 to exit", 'b', 'l', curses.color_pair(1))
        self.pystr(f"{curses.LINES} {curses.COLS}", 't', 'r', curses.A_REVERSE)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
