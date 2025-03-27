import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal

import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        self.bg0 = self.root.new_layer()
        self.bg1 = self.root.new_layer()
        self.img = self.root.new_layer()
        self.txt = self.root.new_layer()

        self.bg0.set_chattr(1, '.', curses.A_BOLD)
        self.bg1.set_chattr(1, ':', curses.A_DIM)
        self.img.set_chattr(1, '#', curses.color_pair(2))

        self.effect0 = np.random.random((curses.LINES, curses.COLS)) < 0.2
        self.effect1 = np.random.random((curses.LINES, curses.COLS)) < 0.2


    # --------------------------------------------------------------------------
    def on_update(self):
        self.bg0.add_block(0, 0, self.effect0)
        self.bg1.add_block(0, 0, self.effect1)
        self.img.load_npy(2, 3, "demos/data/cat.npy")

        self.txt.add_text("Press F1 to exit", 'b', 'l', curses.color_pair(1))
        self.txt.add_text(f"{curses.LINES} {curses.COLS}", 't', 'r', curses.A_REVERSE)


    # --------------------------------------------------------------------------
    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run()


################################################################################
