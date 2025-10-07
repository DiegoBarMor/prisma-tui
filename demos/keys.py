from _mods.allow_root_imports import *
import prismatui as pr

# //////////////////////////////////////////////////////////////////////////////
class TUI(pr.Terminal):
    def on_start(self):
        pr.init_pair(1, pr.COLOR_BLACK, pr.COLOR_CYAN)

    # --------------------------------------------------------------------------
    def on_update(self):
        self.draw_text('c','c', f"{self.h} lines, {self.w} cols", pr.A_REVERSE)
        self.draw_text("c+1",'c', f"Key pressed: {self.key}", pr.A_BOLD)
        self.draw_text('b','l', "Press F1 to exit", pr.get_color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.key == pr.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
