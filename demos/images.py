import prisma
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        self.graphics.load_palette("demos/data/cat.pal")
        prisma.init_pair(1, prisma.COLOR_BLACK, prisma.COLOR_CYAN)

        self.bg0 = self.root.create_layer()
        self.bg1 = self.root.create_layer()
        self.img = self.root.create_layer()
        self.txt = self.root.create_layer()

        shape = prisma.get_size()
        chars_noise_0 = np.full(shape, ' ', dtype = "U1")
        chars_noise_1 = np.full(shape, ' ', dtype = "U1")
        attrs_noise_0 = np.full(shape, prisma.A_NORMAL, dtype = int)
        attrs_noise_1 = np.full(shape, prisma.A_NORMAL, dtype = int)

        noise_0 = np.random.random(shape) < 0.2
        noise_1 = np.random.random(shape) < 0.2
        chars_noise_0[noise_0] = '.'
        chars_noise_1[noise_1] = '`'
        attrs_noise_0[noise_0] = prisma.A_BOLD
        attrs_noise_1[noise_1] = prisma.A_DIM

        self.layer_noise_0 = prisma.Layer(*shape, chars_noise_0, attrs_noise_0)
        self.layer_noise_1 = prisma.Layer(*shape, chars_noise_1, attrs_noise_1)
        self.layer_cat = self.graphics.load_layer("demos/data/cat.pri")

    # --------------------------------------------------------------------------
    def on_update(self):
        self.bg0.draw_layer(0, 0, self.layer_noise_0.copy())
        self.bg1.draw_layer(0, 0, self.layer_noise_1.copy())
        self.img.draw_layer('c', 'c', self.layer_cat.copy())

        self.txt.draw_text('b','l', "Press F1 to exit", prisma.get_color_pair(1))
        self.txt.draw_text('t','r', f"{self.h} {self.w}", prisma.A_REVERSE)


    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == prisma.KEY_F1


################################################################################
if __name__ == "__main__":
    np.random.seed(0)
    tui = TUI()
    tui.run()


################################################################################
