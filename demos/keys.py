import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # --------------------------------------------------------------------------
    def on_update(self):
        self.add_text('c','c', f"{curses.LINES} lines, {curses.COLS} cols", curses.A_REVERSE)
        self.add_text("c+1",'c', f"Key pressed: {self.char}", curses.A_BOLD)
        self.add_text('b','l', "Press F1 to exit", curses.color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
