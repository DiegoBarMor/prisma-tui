import curses
import prisma

# //////////////////////////////////////////////////////////////////////////////
class Box:
    def __init__(self, size, char, attr):
        self.size = size
        self.chars = [[char for _ in range(size)] for _ in range(size)]
        self.attrs = [[attr for _ in range(size)] for _ in range(size)]
        self.y = 0
        self.x = 0
        self.dy = 0
        self.dx = 0

    # --------------------------------------------------------------------------
    def set_pos(self, y, x):
        self.y = y
        self.x = x

    def set_vel(self, dy, dx):
        self.dy = dy
        self.dx = dx

    def get_data(self):
        return self.y, self.x, self.chars, self.attrs

    # --------------------------------------------------------------------------
    def move(self):
        self.y = max(0, min(self.y + self.dy, curses.LINES - self.size))
        self.x = max(0, min(self.x + self.dx, curses.COLS  - self.size))


# //////////////////////////////////////////////////////////////////////////////
class BoxAutonomous(Box):
    def move(self):
        super().move()
        if (self.y == 0) or (self.y == curses.LINES - self.size):
            self.dy = -self.dy
        if (self.x == 0) or (self.x == curses.COLS  - self.size):
            self.dx = -self.dx


# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        size = 5
        self.box_0 = Box(size, '#', curses.A_BOLD)
        self.box_1 = BoxAutonomous(size, '*', curses.A_DIM)

        self.box_0.set_pos(self.h // 2, (self.w - size) // 2)
        self.box_1.set_vel(1, 1)

        self.canvas = self.root.new_layer()

    # --------------------------------------------------------------------------
    def on_update(self):
        match self.char:
            case 119 | curses.KEY_UP:    self.box_0.set_vel(-1,  0)
            case 97  | curses.KEY_LEFT:  self.box_0.set_vel( 0, -1)
            case 115 | curses.KEY_DOWN:  self.box_0.set_vel( 1,  0)
            case 100 | curses.KEY_RIGHT: self.box_0.set_vel( 0,  1)
            case _: self.box_0.set_vel(0, 0)

        self.box_0.move()
        self.box_1.move()

        self.canvas.add_matrix(*self.box_0.get_data())
        self.canvas.add_matrix(*self.box_1.get_data())

        y, x, _, _ = self.box_0.get_data()
        self.add_text('b','r', f"({y}, {x}) {curses.LINES} {curses.COLS}", curses.A_REVERSE)
        self.add_text('b','l', f"Press F1 to exit (current key: {self.char})", curses.color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run(fps = 60)


################################################################################
