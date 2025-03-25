import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        self.bg = self.root.new_layer()
        self.fg = self.root.new_layer()

        self.bg.setchattr(1, '.', curses.A_BOLD)
        self.fg.setchattr(1, '*', curses.color_pair(2))


    def on_update(self):
        self.fg.addimg(2, 3, "demos/data/cat.npy")
        self.pystr("Press F1 to exit", 'b', 'l', curses.color_pair(1))
        self.pystr(f"{curses.LINES} {curses.COLS}", 't', 'r', curses.A_REVERSE)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
