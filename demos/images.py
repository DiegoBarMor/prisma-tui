import curses
import prisma
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        curses.curs_set(False)
        self.graphics.load_palette("demos/data/cat.pal")
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

        self.bg0 = self.root.create_layer()
        self.bg1 = self.root.create_layer()
        self.img = self.root.create_layer()
        self.txt = self.root.create_layer()

        shape = (curses.LINES, curses.COLS)
        chars_noise_0 = np.full(shape, ' ', dtype = "U1")
        chars_noise_1 = np.full(shape, ' ', dtype = "U1")
        attrs_noise_0 = np.full(shape, curses.A_NORMAL, dtype = int)
        attrs_noise_1 = np.full(shape, curses.A_NORMAL, dtype = int)

        noise_0 = np.random.random(shape) < 0.2
        noise_1 = np.random.random(shape) < 0.2
        chars_noise_0[noise_0] = '.'
        chars_noise_1[noise_1] = '`'
        attrs_noise_0[noise_0] = curses.A_BOLD
        attrs_noise_1[noise_1] = curses.A_DIM

        self.mat_noise_0 = prisma.PixelMatrix(*shape, chars_noise_0, attrs_noise_0)
        self.mat_noise_1 = prisma.PixelMatrix(*shape, chars_noise_1, attrs_noise_1)
        self.mat_cat = self.graphics.load_pixel_matrix("demos/data/cat.pri")

    # --------------------------------------------------------------------------
    def on_update(self):
        self.bg0.draw_matrix(0, 0, self.mat_noise_0.copy())
        self.bg1.draw_matrix(0, 0, self.mat_noise_1.copy())
        self.img.draw_matrix('c', 'c', self.mat_cat.copy())

        self.txt.draw_text('b','l', "Press F1 to exit", curses.color_pair(1))
        self.txt.draw_text('t','r', f"{curses.LINES} {curses.COLS}", curses.A_REVERSE)


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run()


################################################################################
