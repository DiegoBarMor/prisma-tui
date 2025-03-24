import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def on_update(self):
        self.pystr(f"{curses.LINES} lines, {curses.COLS} cols", 'c', 'c', curses.A_REVERSE)
        self.pystr(f"Key pressed: {self.char}", self.root.ystr + 1, 'c', curses.A_BOLD)
        self.pystr("Press F1 to exit", 'b', 'l', curses.color_pair(1))

    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
