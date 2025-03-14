import curses
from collections.abc import Callable

from prisma.section import Section


# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    def __init__(self, fps = None):
        self._no_delay: bool
        self._nap_ms: int
        self._wait: Callable
        self.set_fps(fps)

        self._sects = []
        self._running = False
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
            self.stdsect = self.addsect(
                Section(self.stdscr, hauto=True, wauto=True)
            )
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
            curses.update_lines_cols()
            for sect in self._sects: sect.reset()
            self.on_update()
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
    def get_size(self):
        # return curses.LINES, curses.COLS
        return self.stdscr.getmaxyx()

    # --------------------------------------------------------------------------
    def resize(self, h, w):
        print(f"\x1b[8;{h};{w}t")
        for sect in self._sects:
            sect.adjust_size()


    # --------------------------------------------------------------------------
    def addsect(self, section: Section):
        self._sects.append(section)
        return section

    # --------------------------------------------------------------------------
    def pystr(self, *args, **kws): self.stdsect.pystr(*args, **kws)
    def addlayer(self, *args, **kws): self.stdsect.addlayer(*args, **kws)


# //////////////////////////////////////////////////////////////////////////////
