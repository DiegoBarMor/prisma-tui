import curses

from prisma.section import RootSection
from prisma.utils import Debug; d = Debug("terminal.log")

# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    def __init__(self):
        self._no_delay = False
        self._nap_ms = 0
        self._wait = lambda: None
        self._running = False

        self.char = None
        self.stdscr: curses.window
        self.root: RootSection
        self.h = 0
        self.w = 0

    # --------------------------------------------------------------------------
    def on_start(self):
        return

    def on_update(self):
        return

    def on_end(self):
        return

    def kill_when(self):
        return False

    def kill(self):
        self._running = False

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self, fps = None):
        self.set_fps(fps)

        try:
            self.stdscr = curses.initscr()
            curses.noecho(); curses.cbreak()
            self.stdscr.keypad(1)

            try: curses.start_color()
            except: pass

            self.root = RootSection(self.stdscr)
            return self._main_loop()

        finally:
            if "stdscr" not in self.__dict__: return
            self.stdscr.keypad(0)
            curses.echo(); curses.nocbreak()
            curses.endwin()

    # --------------------------------------------------------------------------
    def _main_loop(self):
        self.on_start()
        self.stdscr.nodelay(self._no_delay)

        self._running = True
        while self._running:
            self._handle_resize()

            self.root.clear()
            self.on_update()
            self.root.draw()

            self.char = self.stdscr.getch()
            if self.kill_when(): self.kill()
            self._wait()

        return self.on_end()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_fps(self, fps):
        if fps is None:
            self._no_delay = False
            self._nap_ms = 0
            self._wait = lambda: None
        else:
            self._no_delay = True
            self._nap_ms = int(1000 / fps)
            self._wait = lambda: curses.napms(self._nap_ms)

    # --------------------------------------------------------------------------
    def _handle_resize(self):
        curses.update_lines_cols()
        h, w = curses.LINES, curses.COLS

        if (self.h == h) and (self.w == w): return

        self.h = h; self.w = w
        self.root.set_size(h, w)

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        print(f"\x1b[8;{h};{w}t")
        self._handle_resize()

    # --------------------------------------------------------------------------
    def add_text(self, *args, **kws): self.root.add_text(*args, **kws)
    def draw_layers(self, *args, **kws): self.root.draw_layers(*args, **kws)


# //////////////////////////////////////////////////////////////////////////////
