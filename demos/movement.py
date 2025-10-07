import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class Box:
    def __init__(self, size, char, attr):
        self.size = size
        self.layer = pr.Layer(
            size, size,
            chars = [[char for _ in range(size)] for _ in range(size)],
            attrs = [[attr for _ in range(size)] for _ in range(size)]
        )
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
        return self.y, self.x, self.layer

    # --------------------------------------------------------------------------
    def move(self, lines, cols):
        self.y = max(0, min(self.y + self.dy, lines - self.size))
        self.x = max(0, min(self.x + self.dx, cols  - self.size))


# //////////////////////////////////////////////////////////////////////////////
class BoxAutonomous(Box):
    def move(self, lines, cols):
        super().move(lines, cols)
        if (self.y == 0) or (self.y == lines - self.size):
            self.dy = -self.dy
        if (self.x == 0) or (self.x == cols  - self.size):
            self.dx = -self.dx


# //////////////////////////////////////////////////////////////////////////////
class TUI(pr.Terminal):
    def on_start(self):
        pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

        size = 5
        self.box_0 = Box(size, '#', pr.A_BOLD)
        self.box_1 = BoxAutonomous(size, '*', pr.A_DIM)

        self.box_0.set_pos(self.h // 2, (self.w - size) // 2)
        self.box_1.set_vel(1, 1)

        self.canvas = self.root.create_layer()

    # --------------------------------------------------------------------------
    def on_update(self):
        match self.key:
            case 119 | pr.KEY_UP:    self.box_0.set_vel(-1,  0)
            case 97  | pr.KEY_LEFT:  self.box_0.set_vel( 0, -1)
            case 115 | pr.KEY_DOWN:  self.box_0.set_vel( 1,  0)
            case 100 | pr.KEY_RIGHT: self.box_0.set_vel( 0,  1)
            case _: self.box_0.set_vel(0, 0)

        self.box_0.move(self.h, self.w)
        self.box_1.move(self.h, self.w)

        self.canvas.draw_layer(*self.box_0.get_data())
        self.canvas.draw_layer(*self.box_1.get_data())

        y, x, _ = self.box_0.get_data()
        self.draw_text('b','l', f"Press F1 to exit", pr.get_color_pair(1))
        self.draw_text('b-1','c', "Use arrow keys or WASD to move the white box")
        self.draw_text('b','r', f"({y}, {x}) {self.h} {self.w}", pr.A_REVERSE)

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run(fps = 60)


################################################################################
