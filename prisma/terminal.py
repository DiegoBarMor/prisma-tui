import curses
import numpy as np
from collections.abc import Callable

from prisma.section import Section


# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    def __init__(self, fps = None):
        self._no_delay: bool
        self._nap_ms: int
        self._wait: Callable
        self.set_fps(fps)

        self._running = False
        self._sects = []
        self.char = None

        self.stdscr: curses.window
        self.stdsect: Section

    # --------------------------------------------------------------------------
    def on_init(self):
        return # override!

    def on_update(self):
        return # override!

    def on_end(self):
        return # override!

    def kill_when(self):
        return True # override!

    def kill(self):
        self._running = False

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self):
        try:
            self.stdscr = curses.initscr()
            self.stdsect = Section(self.stdscr)
            self.addsect(self.stdsect)
            curses.noecho()
            curses.cbreak()
            self.stdscr.keypad(1)
            try: curses.start_color()
            except: pass
            return self.main()

        finally:
            if "stdscr" not in self.__dict__: return
            self.stdscr.keypad(0)
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    # --------------------------------------------------------------------------
    def main(self):
        self.stdscr.nodelay(self._no_delay)
        self.on_init()
        self._running = True
        while self._running:
            self.y = 0
            self.x = 0
            curses.update_lines_cols()
            # map(lambda sect: sect.erase(), self._sects)
            for sect in self._sects: sect.erase()
            self.on_update()
            # map(lambda sect: sect.draw(), self._sects)
            for sect in self._sects: sect.draw()
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
            self._wait = lambda: curses.napm(self._nap_ms)

    # --------------------------------------------------------------------------
    def addsect(self, section: Section):
        self._sects.append(section)

    # --------------------------------------------------------------------------
    def pystr(self, *args, **kws): self.stdsect.pystr(*args, **kws)
    def addlayer(self, *args, **kws): self.stdsect.addlayer(*args, **kws)


# //////////////////////////////////////////////////////////////////////////////
