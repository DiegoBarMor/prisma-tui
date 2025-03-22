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

        self.root.mosaic('\n'.join([
            "aaab",
            "aaab",
            "ccdd",
            "ccdd",
        ]))
        self.canvas = self.root.get_child('a')
        self.rpanel = self.root.get_child('b')
        self.bpanel = self.root.get_child('c')
        self.overlay = self.root.add_child(
            "overlay", Section((2, self.root.w, self.root.h - 2, 0))           
        )

    def on_update(self):
        h,w = self.root.get_size()
        match self.char:
            case curses.KEY_UP:    h -= 1
            case curses.KEY_LEFT:  w -= 1
            case curses.KEY_DOWN:  h += 1
            case curses.KEY_RIGHT: w += 1
        # self.root.set_size(h, w)

        self.stdscr.border()
        # self.canvas.border()
        # self.rpanel.border()
        for sect in self.root._children.values():
            sect.border()
            # pass



        # self.canvas.pystr('c'*10000, 't', 'l')
        # self.rpanel.pystr('r'*10000, 't', 'l')
        # self.bpanel.pystr('b'*10000, 't', 'l')
        # self.canvas.pystr(f"CANVAS: {self.canvas._win.getmaxyx()}", 'c', 'c')
        # self.rpanel.pystr(f"RPANEL: {self.rpanel._win.getmaxyx()}", 'c', 'c')
        # self.bpanel.pystr(f"BPANEL: {self.bpanel._win.getmaxyx()}", 'c', 'c')

        for char,sect in self.root._children.items():
            sect.pystr(f"{char}: {sect._win.getmaxyx()}", 'c', 'c')

        self.overlay.pystr("Resize the screen with the arrow keys", 0, 'l', curses.color_pair(1))
        self.overlay.pystr("Press F1 to exit", 1, 'l', curses.color_pair(1))

        self.overlay.pystr(f"{curses.LINES} {curses.COLS}", 1, 'r', curses.A_REVERSE)


    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
