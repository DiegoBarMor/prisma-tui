import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def on_update(self):
        self.add_text(f"{curses.LINES} lines, {curses.COLS} cols", 'C', 'C', curses.A_REVERSE)
        self.add_text(f"Key pressed: {self.char}", "C+1", 'C', curses.A_BOLD)
        self.add_text("Press F1 to exit", 'B', 'L', curses.color_pair(1))

    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
