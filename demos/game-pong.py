import time
import curses
import prisma
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Actor:
    def __init__(self, h, w):
        self.h = h
        self.w = w
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

    # --------------------------------------------------------------------------
    def move(self, boundaries):
        ymin, xmin, ymax, xmax = boundaries
        self.y = round(max(ymin, min(self.y + self.dy, ymax)))
        self.x = round(max(xmin, min(self.x + self.dx, xmax)))

    def stamp_to_field(self, field: "Field"):
        pass

    def get_size_pos(self):
        return self.h, self.w, self.y, self.x

class Ball(Actor):
    def move(self, boundaries):
        super().move(boundaries)
        ymin, _, ymax, _ = boundaries
        abs_dy = 1 if self.dy > 0 else -1
        if not (ymin-1 < self.y + abs_dy < ymax+1):
            self.dy = -self.dy

    def reset(self):
        pass


# //////////////////////////////////////////////////////////////////////////////
class Field:
    EMPTY_SPACE = 0
    DANGER_ZONE = 1
    PLAYER_PAD = 2
    BALL = 3

    PAD_H = 5
    PAD_W = 2
    PAD_X = 3
    BALL_R = 2
    SCORE_TO_WIN = 5

    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.score0 = 0
        self.score1 = 0

        self._arr = np.zeros((h, w))
        self._char_map = [' ', ' ', '+', '#']
        self._attr_map = [0, curses.color_pair(2), curses.A_BOLD, curses.A_BOLD]

        self.p0_x = self.PAD_X
        self.p1_x = self.w - (self.PAD_X + self.PAD_W)

        self._player0 = Actor(self.PAD_H, self.PAD_W)
        self._player0.set_pos( 5, self.p0_x)

        self._player1  = Actor(self.PAD_H, self.PAD_W)
        self._player1.set_pos( 5, self.p1_x)

        self._ball = Ball(self.BALL_R, self.BALL_R)
        self._next_round()


    def handle_input(self, key):
        match key:
            case 119 | curses.KEY_UP:
                dy = -1
                self._player0.set_vel(dy,  0)
            case 115 | curses.KEY_DOWN:
                dy = 1
                self._player0.set_vel(dy,  0)
            case -1: pass
            case _: self._player0.set_vel(0,  0)



    def _slice_arr(self, h, w, y, x):
        return self._arr[y:y+h, x:x+w]

    def _update_score(self):
        if self._ball.x > self.w // 2:
            self.score0 += 1
        else:
            self.score1 += 1


    def _next_round(self):
        if self._ball.x > self.w // 2:
            dx_init = -1
        else:
            dx_init = 1

        dy_init = np.random.random() * 2

        self._ball.set_pos(
            (self.h - self.BALL_R) // 2,
            (self.w - self.BALL_R) // 2
        )
        self._ball.set_vel(dy_init, dx_init)

    def update(self):
        boundaries_pad = (1, 1,
            self.h - (self.PAD_H + 1),
            self.w - (self.PAD_W + 1)
        )
        boundaries_ball = (1, 1,
            self.h - (self.BALL_R + 1),
            self.w - (self.BALL_R + 1)
        )

        self._player0.move(boundaries_pad)
        self._player1.move(boundaries_pad)
        self._ball.move(boundaries_ball)


        arr_d0 = self._slice_arr(self.h, self.PAD_W, 0, self.p0_x)
        arr_d1 = self._slice_arr(self.h, self.PAD_W, 0, self.p1_x)
        arr_p0 = self._slice_arr(*self._player0.get_size_pos())
        arr_p1 = self._slice_arr(*self._player1.get_size_pos())
        arr_ba = self._slice_arr(*self._ball.get_size_pos())


        if np.any(arr_ba == self.PLAYER_PAD):
            self._ball.dx = -self._ball.dx
            self._ball.move(boundaries_ball) # avoid cliping with pad

        if np.any(arr_ba == self.DANGER_ZONE):
            self._update_score()
            self._next_round()


        self._arr.fill(0)
        arr_d0.fill(self.DANGER_ZONE)
        arr_d1.fill(self.DANGER_ZONE)
        arr_p0.fill(self.PLAYER_PAD)
        arr_p1.fill(self.PLAYER_PAD)
        arr_ba.fill(self.BALL)


    def get_matrix(self):
        return prisma.PixelMatrix(
            *self._arr.shape,
            chars = [[self._char_map[int(i)] for i in row] for row in self._arr],
            attrs = [[self._attr_map[int(i)] for i in row] for row in self._arr]
        )



# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        curses.curs_set(False)
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)

        self.canvas = self.root.create_child(0.8, 1.0, 0.2, 0)
        self.first_iter = True

    # --------------------------------------------------------------------------
    def on_update(self):
        if self.first_iter:
            self.field = Field(*self.canvas.get_size())
            self.first_iter = False

        self.field.handle_input(self.char)
        self.field.update()

        self.canvas.draw_matrix(0,0,self.field.get_matrix())
        self.canvas.draw_border()

        score_y = max(0, self.canvas.y - 2)

        self.draw_text(score_y, 'c', "SCORE")
        self.draw_text(score_y+1, 'c', f"{self.field.score0} : {self.field.score1}")
        self.draw_text('b','r', f"({curses.LINES} {curses.COLS}", curses.A_REVERSE)
        self.draw_text('b','l', f"Press F1 to exit (current key: {self.char})", curses.color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run(fps = 60)


################################################################################
