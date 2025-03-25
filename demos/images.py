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
        shape = (curses.LINES, curses.COLS)

        self.bg.set_size(*shape)
        self.bg.arr = ~self.bg.arr

        self.fg.set_size(*shape)
        self.fg.addimg("demos/data/cat.npy", 2, 3)

        self.draw_layers()

        self.pystr("Press F1 to exit", 'b', 'l', curses.color_pair(1))
        self.pystr(f"{curses.LINES} {curses.COLS}", 't', 'r', curses.A_REVERSE)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
