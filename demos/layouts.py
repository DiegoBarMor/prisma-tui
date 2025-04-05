import curses
import prisma

# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    # --------------------------------------------------------------------------
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_YELLOW)

        self.names = ["canvas", "tpanel", "bpanel", "lpanel", "rpanel"]

        self.canvas = self.root.add_child(-6, -10, 3, 5)
        self.tpanel = self.root.add_child(3, 1.0,  0, 0)
        self.bpanel = self.root.add_child(3, 1.0, -3, 0)
        self.lpanel = self.root.add_child(-6, 5, 3, 0 )
        self.rpanel = self.root.add_child(-6, 5, 3, -3)

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
            case curses.KEY_UP:    self.set_size(h-1, w  )
            case curses.KEY_LEFT:  self.set_size(h  , w-1)
            case curses.KEY_DOWN:  self.set_size(h+1, w  )
            case curses.KEY_RIGHT: self.set_size(h  , w+1)


        for name,sect in zip(self.names, self.canvas.iter_children()):
            sect.add_text('c','c', f"{name}: {sect.get_size()}, {sect.get_pos()}")

        self.tpanel.add_text('c','c', "TOP")
        self.bpanel.add_text('c','c', "BOTTOM")
        self.lpanel.add_text('c','c', '\n'.join("LEFT"))
        self.rpanel.add_text('c','c', '\n'.join("RIGHT"))

        for sect in self.root.iter_children():
            if sect is self.canvas: continue
            sect.add_border()
        for sect in self.canvas.iter_children():
            sect.add_border()

        self.bpanel.add_text('t','l', "Resize the screen with the arrow keys", curses.color_pair(1), transparency = 0)
        self.bpanel.add_text('t+1','l', "Press F1 to exit", curses.color_pair(1), transparency = 0)
        self.bpanel.add_text('t+1','r', f"{curses.LINES} {curses.COLS}", curses.A_REVERSE, transparency = 0)

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
