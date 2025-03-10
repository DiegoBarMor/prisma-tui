import curses

from prisma import Prisma, Align

# //////////////////////////////////////////////////////////////////////////////
class TUI(Prisma):
    def on_init(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    def on_update(self):
        self.pystr(
            f"{curses.LINES} lines, {curses.COLS} cols",
            curses.A_REVERSE, Align.YCENTER | Align.XCENTER
        )

        self.y += 1
        self.pystr(f"Key pressed: {self.char}", curses.A_BOLD, Align.XCENTER)

        self.pystr("Press F1 to exit", curses.color_pair(1), Align.YBOTTOM | Align.XLEFT)

    def kill_when(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
