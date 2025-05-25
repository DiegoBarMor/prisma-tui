import prisma

# //////////////////////////////////////////////////////////////////////////////
class TUI(prisma.Terminal):
    def on_start(self):
        prisma.init_pair(1, prisma.COLOR_BLACK, prisma.COLOR_CYAN)

    # --------------------------------------------------------------------------
    def on_update(self):
        self.draw_text('c','c', f"{self.h} lines, {self.w} cols", prisma.A_REVERSE)
        self.draw_text("c+1",'c', f"Key pressed: {self.char}", prisma.A_BOLD)
        self.draw_text('b','l', "Press F1 to exit", prisma.get_color_pair(1))

    # --------------------------------------------------------------------------
    def should_stop(self):
        return self.char == prisma.KEY_F1


################################################################################
if __name__ == "__main__":
    tui = TUI()
    tui.run()


################################################################################
