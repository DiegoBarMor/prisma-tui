from _mods.allow_root_imports import *
import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class TUI(pr.Terminal):
    def on_start(self):
        pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)
        pr.init_pair(2, pr.COLOR_BLACK, pr.COLOR_YELLOW)

        self.names = ["canvas", "tpanel", "bpanel", "lpanel", "rpanel"]

        self.canvas = self.root.create_child(-6, -10, 3, 5)
        self.tpanel = self.root.create_child(3, 1.0,  0, 0)
        self.bpanel = self.root.create_child(3, 1.0, -3, 0)
        self.lpanel = self.root.create_child(-6, 5, 3, 0 )
        self.rpanel = self.root.create_child(-6, 5, 3, -3)

        self.canvas.create_mosaic('\n'.join([
            "aaab",
            "aaab",
            "ccdd",
            "ccdd",
        ]))

    # --------------------------------------------------------------------------
    def on_update(self):
        h,w = self.root.get_size()
        match self.key:
            case pr.KEY_UP:    self.resize_terminal(h-1, w  )
            case pr.KEY_LEFT:  self.resize_terminal(h  , w-1)
            case pr.KEY_DOWN:  self.resize_terminal(h+1, w  )
            case pr.KEY_RIGHT: self.resize_terminal(h  , w+1)


        for name,sect in zip(self.names, self.canvas.iter_children()):
            sect.draw_text('c','c', f"{name}: {sect.get_size()}, {sect.get_position()}")

        self.tpanel.draw_text('c','c', "TOP")
        self.bpanel.draw_text('c','c', "BOTTOM")
        self.lpanel.draw_text('c','c', '\n'.join("LEFT"))
        self.rpanel.draw_text('c','c', '\n'.join("RIGHT"))

        for sect in self.root.iter_children():
            if sect is self.canvas: continue
            sect.draw_border()
        for sect in self.canvas.iter_children():
            sect.draw_border()

        self.bpanel.draw_text('t','l', "Resize the screen with the arrow keys", pr.get_color_pair(1), pr.BlendMode.OVERWRITE)
        self.bpanel.draw_text('t+1','l', "Press F1 to exit", pr.get_color_pair(1), pr.BlendMode.OVERWRITE)
        self.bpanel.draw_text('t+1','r', f"{self.h} {self.w}", pr.A_REVERSE, pr.BlendMode.OVERWRITE)

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
