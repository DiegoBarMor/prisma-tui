import curses

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.terminal import Terminal
from prisma.section import Section

# //////////////////////////////////////////////////////////////////////////////
class TUI(Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        self.names = ["canvas", "tpanel", "bpanel", "lpanel", "rpanel"]

        self.canvas = self.root.add_child(Section(-6, -10, 3, 5))
        self.tpanel = self.root.add_child(Section(3, 1.0,  0, 0))
        self.bpanel = self.root.add_child(Section(3, 1.0, -3, 0))
        self.lpanel = self.root.add_child(Section(-6, 5, 3, 0 ))
        self.rpanel = self.root.add_child(Section(-6, 5, 3, -3))

        self.canvas.mosaic('\n'.join([
            "aaab",
            "aaab",
            "ccdd",
            "ccdd",
        ]))

    # --------------------------------------------------------------------------
    def on_update(self):
        h,w = self.root.get_size()
        match self.char:
            case curses.KEY_UP:    self.set_size(h - 1, w    )
            case curses.KEY_LEFT:  self.set_size(h    , w - 1)
            case curses.KEY_DOWN:  self.set_size(h + 1, w    )
            case curses.KEY_RIGHT: self.set_size(h    , w + 1)

        for name,sect in zip(self.names, self.canvas.iter_children()):
            sect.add_text(f"{name}: {sect._win.getmaxyx()}, {sect._win.getbegyx()}", 'c', 'c')

        self.tpanel.add_text("TOP", 'c', 'c')
        self.bpanel.add_text("BOTTOM", 'c', 'c')
        self.lpanel.add_text('\n'.join("LEFT"), 'c', 'c')
        self.rpanel.add_text('\n'.join("RIGHT"), 'c', 'c')

        for sect in self.root.iter_children():
            if sect is self.canvas: continue
            sect.do_border(last = False)
        for sect in self.canvas.iter_children():
            sect.do_border()

        self.bpanel.add_text("Resize the screen with the arrow keys", 0, 'l', curses.color_pair(1), transparency = 0)
        self.bpanel.add_text("Press F1 to exit", 1, 'l', curses.color_pair(1), transparency = 0)
        self.bpanel.add_text(f"{curses.LINES} {curses.COLS}", 1, 'r', curses.A_REVERSE, transparency = 0)


    # --------------------------------------------------------------------------
    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
