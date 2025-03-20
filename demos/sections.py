import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal
from prisma.section import Section

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_init(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        hcanvas = 30
        wcanvas = 50

        self.canvas = self.addsect(
            Section.newwin(h=hcanvas, w=wcanvas, y=0, x=0)
        )
        self.rpanel = self.addsect(
            Section.newwin(h=hcanvas, w=0, y=0, x=wcanvas)
        )

        self.stdsect.hlayout()
        self.stdsect.addchild(self.canvas)
        self.stdsect.addchild(self.rpanel)

    def on_update(self):
        h,w = self.get_size()
        match self.char:
            case curses.KEY_UP:    h -= 1
            case curses.KEY_LEFT:  w -= 1
            case curses.KEY_DOWN:  h += 1
            case curses.KEY_RIGHT: w += 1
        self.resize(h, w)

        self.stdscr.border()
        self.canvas.border()
        self.rpanel.border()

        self.pystr("Resize the screen with the arrow keys", 'b', 'l', curses.color_pair(1))
        self.pystr("Press F1 to exit", self.stdsect.ystr-1, 'l', curses.color_pair(1))
        self.pystr(f"{curses.LINES} {curses.COLS}", 'b', 'r', curses.A_REVERSE)
        self.canvas.pystr(f"CANVAS: {self.canvas._win.getmaxyx()}", 'c', 'c')
        self.rpanel.pystr(f"CANVAS: {self.rpanel._win.getmaxyx()}", 'c', 'c')


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
