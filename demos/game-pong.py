import time
import prisma
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Actor:
    def __init__(self, h, w, field):
        self.h = h
        self.w = w
        self.y = 0
        self.x = 0
        self.dy = 0
        self.dx = 0
        self._y_float = 0.0
        self._x_float = 0.0
        self.field = field
        self.in_motion = True

    # --------------------------------------------------------------------------
    def set_pos(self, y, x):
        self.y = self._y_float = y
        self.x = self._x_float = x

    def set_vel(self, dy, dx):
        self.dy = dy
        self.dx = dx

    def get_pos(self):
        return self.y, self.x

    def get_size_pos(self):
        return self.h, self.w, self.y, self.x

    def get_real_pos(self):
        return self._y_float, self._x_float

    # --------------------------------------------------------------------------
    def update(self, boundaries):
        if not self.in_motion: return
        ymin, xmin, ymax, xmax = boundaries
        self._y_float = max(ymin, min(self._y_float + self.dy, ymax))
        self._x_float = max(xmin, min(self._x_float + self.dx, xmax))
        self.y = round(self._y_float)
        self.x = round(self._x_float)

    def handle_input(self, key):
        return


# //////////////////////////////////////////////////////////////////////////////
class Ball(Actor):
    YSPEED_MULTIPLIER = 4.0 # 2.0

    def update(self, boundaries):
        super().update(boundaries)
        ymin, _, ymax, _ = boundaries
        abs_dy = 1 if self.dy > 0 else -1
        if not (ymin-1 < self.y + abs_dy < ymax+1):
            self.dy = -self.dy

    def reset(self):
        pass

    def randomize_dy(self):
        self.dy = (np.random.random()-0.5) * self.YSPEED_MULTIPLIER


class Pad(Actor):
    def update(self, boundaries, ball):
        super().update(boundaries)


class PC(Pad):
    def handle_input(self, key):
        match key:
            case 119 | prisma.KEY_UP:
                dy = -1
                self.set_vel(dy,  0)
            case 115 | prisma.KEY_DOWN:
                dy = 1
                self.set_vel(dy,  0)
            case -1: pass
            case _: self.set_vel(0,  0)

class NPC(Pad):
    # MAX_MISCALCUL = 1
    def update(self, boundaries, ball):
        self.ai(ball)
        super().update(boundaries, ball)

    def ai(self, ball):
        # miscalculation = np.random.randint(self.MAX_MISCALCUL + 1)
        return


class NPCNaiveAI(NPC):
    """
    NPC that naively moves towards the current position of the ball. It will naturally fail if the ball is moving fast enough.
    """
    def ai(self, ball):
        diff_y = ball.y - self.y
        self.dy = np.sign(diff_y)

class NPCPredictiveAI(NPC):
    """
    NPC that predicts the final position of the ball (based on its current velocities) and moves there in anticipation.
    """
    def __init__(self, *args, **kwds):
        super().__init__(*args, **kwds)
        self.last_ball_x = 0
        self.debug = []

    def ai(self, ball):
        def r(n): return None if n is None else round(n,2)

        y0, x0 = ball.get_real_pos()

        x1 = (self.x - ball.w) if ball.dx > 0 else (self.x + self.w)

        ymax = self.field.h - ball.h

        last_dist_x = abs(x1 - self.last_ball_x)
        dist_x = abs(x1 - x0)
        self.last_ball_x = ball.x

        self.debug.clear()


        if dist_x > last_dist_x or not ball.in_motion:
            ### either ball going away, it's the other player's turn
            ### or countdown is in progress, so pad goes back to starting position
            y1 = (2 + ymax - self.h) // 2 # add 2 to account for borders
            self.dy = np.sign(y1 - self.y)
            steps = None
            y1_overshoot = None
            bounces = None
            # diff_y = y1 - self._y_float
            # self.dy = np.sign(round(diff_y))
            return

        if ball.dy < 0:
            ### instead of dealing with possibly y1_overshoot < 0,
            ### it's more convenient to deal with a "mirrored" version of y
            y0 = ymax - y0


        steps = dist_x // abs(ball.dx)
        y1_overshoot = y0 + steps * (abs(ball.dy))
        # y1_overshoot = y0 + steps * abs(ball.dy)

        bounces = int(abs(y1_overshoot) // ymax)
        # y1 = y1_overshoot - bounces*(ymax - ball.h) # -2 to account for border?
        y1 = y1_overshoot - bounces*ymax

        if ball.dy < 0: # revert the mirroring of y from above
            y1 = ymax - y1

        if bounces % 2: # must mirror y when there is an odd number of bounces
            y1 = ymax - y1

        self.dy = np.sign(round(y1 - self._y_float))

        self.debug.extend([
            r(ball.y),
            r(self.y),
            r(y1),
            r(y1_overshoot),
            bounces,
            r(- bounces*(ymax))
            # r(- bounces*(ymax - ball.h))
        ])


# //////////////////////////////////////////////////////////////////////////////
class Overlay:
    def __init__(self):
        h = 5; w = 5
        chars_3 = [
            "33333",
            "   33",
            "33333",
            "   33",
            "33333",
        ]
        chars_2 = [
            "22222",
            "   22",
            "22222",
            "22   ",
            "22222",
        ]
        chars_1 = [
            "   11",
            "   11",
            "   11",
            "   11",
            "   11",
        ]
        attrs = [[0 for _ in range(w)] for _ in range(h)]

        self._empty = prisma.Layer(0,0)
        self._number_3 = prisma.Layer(h, w, chars_3, attrs, prisma.BlendMode.OVERWRITE)
        self._number_2 = prisma.Layer(h, w, chars_2, attrs, prisma.BlendMode.OVERWRITE)
        self._number_1 = prisma.Layer(h, w, chars_1, attrs, prisma.BlendMode.OVERWRITE)

    def display_num(self, n):
        match n:
            case 3: return self._number_3
            case 2: return self._number_2
            case 1: return self._number_1
            case 0: return self._empty


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
    BALL_DX = 1 # 0.5
    BALL_DY_MAX = 4 # 2

    SCORE_TO_WIN = 5

    WAIT_SECONDS = 3

    def __init__(self, h, w):
        self.h = h - 1 # substract 1 from dimensions to account for borders
        self.w = w - 1
        self.score0 = 0
        self.score1 = 0

        self._time = time.time()

        self._arr = np.zeros((h, w))
        self._char_map = [' ', ' ', '+', '#', '*']
        self._attr_map = [0, prisma.get_color_pair(2), prisma.A_BOLD, prisma.A_BOLD, prisma.get_color_pair(2)]

        self.p0_x = self.PAD_X
        self.p1_x = self.w - (self.PAD_X + self.PAD_W)

        self._player0 = NPCPredictiveAI(self.PAD_H, self.PAD_W, self)
        self._player0.set_pos( 5, self.p0_x)

        self._player1 = NPCPredictiveAI(self.PAD_H, self.PAD_W, self)
        self._player1.set_pos( 5, self.p1_x)

        self._ball = Ball(self.BALL_R, self.BALL_R, self)
        self._next_round()

        self._overlay = Overlay()



    def handle_input(self, key):
        self._player0.handle_input(key)
        self._player1.handle_input(key)



    def _slice_arr(self, h, w, y, x):
        return self._arr[y:y+h, x:x+w]

    def _update_score(self):
        if self._ball.x > self.w // 2:
            self.score0 += 1
        else:
            self.score1 += 1


    def _next_round(self):
        if self._ball.x > self.w // 2:
            dx_init = -self.BALL_DX
        else:
            dx_init = self.BALL_DX

        self._ball.set_pos(
            (self.h - self.BALL_R) // 2,
            (self.w - self.BALL_R) // 2
        )
        self._ball.randomize_dy()
        self._ball.dx = dx_init
        self._time = time.time()

        self._overlay_num = 0

    def update(self):


        boundaries_pad = (1, 1,
            self.h - (self.PAD_H),
            self.w - (self.PAD_W)
        )
        boundaries_ball = (1, 1,
            self.h - (self.BALL_R),
            self.w - (self.BALL_R)
        )

        self._player1.update(boundaries_pad, self._ball)
        self._player0.update(boundaries_pad, self._ball)

        dt = time.time() - self._time
        self._ball.in_motion = dt > self.WAIT_SECONDS
        self._ball.update(boundaries_ball)

        self._overlay_num = round(max(0, self.WAIT_SECONDS - dt))

        arr_d0 = self._slice_arr(self.h, self.PAD_W, 0, self.p0_x)
        arr_d1 = self._slice_arr(self.h, self.PAD_W, 0, self.p1_x)
        arr_p0 = self._slice_arr(*self._player0.get_size_pos())
        arr_p1 = self._slice_arr(*self._player1.get_size_pos())
        arr_ba = self._slice_arr(*self._ball.get_size_pos())


        if np.any(arr_ba == self.PLAYER_PAD):
            self._ball.randomize_dy()
            self._ball.dx = -self._ball.dx
            self._ball.update(boundaries_ball) # avoid cliping with pad

        elif np.any(arr_ba == self.DANGER_ZONE):
            self._update_score()
            self._next_round()


        self._arr.fill(0)
        arr_d0.fill(self.DANGER_ZONE)
        arr_d1.fill(self.DANGER_ZONE)
        arr_p0.fill(self.PLAYER_PAD)
        arr_p1.fill(self.PLAYER_PAD)
        arr_ba.fill(self.BALL)


    def get_matrix(self):
        base = prisma.Layer(
            *self._arr.shape,
            chars = [[self._char_map[int(i)] for i in row] for row in self._arr],
            attrs = [[self._attr_map[int(i)] for i in row] for row in self._arr]
        )
        layer = self._overlay.display_num(self._overlay_num)
        y_overlay = (self.h - layer.h) // 2
        x_overlay = (self.w - layer.w) // 2
        base.draw_layer(y_overlay, x_overlay, layer)
        return base


# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        prisma.init_pair(1, prisma.COLOR_BLACK, prisma.COLOR_CYAN)
        prisma.init_pair(2, prisma.COLOR_BLACK, prisma.COLOR_GREEN)

        self.canvas = self.root.create_child(-3, 1.0, 2, 0)
        self.field = None

    # --------------------------------------------------------------------------
    def on_update(self):
        if self.field is None:
            self.field = Field(*self.canvas.get_size())

        self.field.handle_input(self.char)
        self.field.update()

        self.canvas.draw_layer(0,0,self.field.get_matrix())
        self.canvas.draw_border()

        score_y = max(0, self.canvas.y - 2)

        self.draw_text(score_y, 'c', "SCORE")
        self.draw_text(score_y+1, 'c', f"{self.field.score0} : {self.field.score1}")
        self.draw_text('b','r', f"({self.h} {self.w}", prisma.A_REVERSE)
        self.draw_text('b','l', f"Press F1 to exit (current key: {self.char})", prisma.get_color_pair(1))

        d0 = self.field._player0.debug
        d1 = self.field._player1.debug
        self.draw_text(0,0, f"{d0}", blend = prisma.BlendMode.OVERWRITE)
        self.draw_text(1,0, f"{d1}", blend = prisma.BlendMode.OVERWRITE)


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == prisma.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run(fps = 10)


################################################################################
