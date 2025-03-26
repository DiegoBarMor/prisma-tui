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

        self.bg = self.root.new_layer()
        self.overlay0 = self.root.new_layer()
        self.overlay1 = self.root.new_layer()
        self.fg = self.root.new_layer()
        self.text = self.root.new_layer()

        self.bg.set_chattr(1, '.', curses.A_BOLD)
        self.fg.set_chattr(1, '*', curses.color_pair(2))

        # self.effect0 = ~np.tril(np.ones((curses.LINES, curses.COLS), dtype = bool))
        # self.overlay0.set_chattr(1, ' ', curses.A_UNDERLINE)

        # self.effect0 = np.random.random((curses.LINES, curses.COLS)) > 0.2
        # self.overlay0.set_chattr(1, '~', curses.A_DIM)

        self.effect0 = np.random.random((curses.LINES, curses.COLS)) > 0.2
        self.effect1 = np.random.random((curses.LINES, curses.COLS)) > 0.2
        self.overlay0.set_chattr(1, '~', curses.A_BOLD)
        self.overlay1.set_chattr(1, '.', curses.A_DIM)


    def on_update(self):
        # self.bg.fill_matrix('.')
        self.fg.add_img(2, 3, "demos/data/cat.npy")
        self.overlay0.add_img(0, 0, self.effect0)
        self.overlay1.add_img(0, 0, self.effect1)

        self.text.add_text("Press F1 to exit", 'b', 'l', curses.color_pair(1))
        self.text.add_text(f"{curses.LINES} {curses.COLS}", 't', 'r', curses.A_REVERSE)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
