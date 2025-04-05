import curses
import prisma
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        curses.curs_set(False)

        self.bg0 = self.root.new_layer()
        self.bg1 = self.root.new_layer()
        self.img = self.root.new_layer()
        self.txt = self.root.new_layer()

        self.graphics.load_palette("demos/data/cat.pal")
        self.chars_cat, self.attrs_cat = self.graphics.load_pri("demos/data/cat.pri")

        noise_0 = np.random.random((curses.LINES, curses.COLS)) < 0.2
        noise_1 = np.random.random((curses.LINES, curses.COLS)) < 0.2

        self.chars_noise_0 = np.full_like(noise_0, ' ', dtype = "U1")
        self.attrs_noise_0 = np.full_like(noise_0, curses.A_NORMAL, dtype = int)
        self.chars_noise_0[noise_0] = '.'
        self.attrs_noise_0[noise_0] = curses.A_BOLD

        self.chars_noise_1 = np.full_like(noise_1, ' ', dtype = "U1")
        self.attrs_noise_1 = np.full_like(noise_1, curses.A_NORMAL, dtype = int)
        self.chars_noise_1[noise_1] = '`'
        self.attrs_noise_1[noise_1] = curses.A_DIM
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)

    # --------------------------------------------------------------------------
    def on_update(self):
        self.bg0.add_matrix(0, 0, self.chars_noise_0, self.attrs_noise_0)
        self.bg1.add_matrix(0, 0, self.chars_noise_1, self.attrs_noise_1)
        self.img.add_matrix('c', 'c', self.chars_cat, self.attrs_cat)

        self.txt.add_text('b','l', "Press F1 to exit", curses.color_pair(1))
        self.txt.add_text('t','r', f"{curses.LINES} {curses.COLS}", curses.A_REVERSE)


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == curses.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run()


################################################################################
