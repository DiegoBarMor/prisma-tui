import curses
import prisma

# //////////////////////////////////////////////////////////////////////////////
class Terminal:
    # --------------------------------------------------------------------------
    def __init__(self):
        self.h: int = 0
        self.w: int = 0
        self.char: int = -1
        self.root: prisma.Section
        self.stdscr: curses.window
        self.graphics: prisma.Graphics

        self._no_delay: bool = False
        self._nap_ms: int = 0
        self._wait = lambda: None
        self._running: bool = False


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _internal_on_start(self) -> None:
        self.root = prisma.Section()
        self.graphics = prisma.Graphics()
        self._running = True
        self.stdscr.nodelay(self._no_delay)
        self.on_start()

    # --------------------------------------------------------------------------
    def _internal_on_resize(self) -> None:
        curses.update_lines_cols()
        h, w = curses.LINES, curses.COLS

        if (self.h == h) and (self.w == w): return

        self.h = h; self.w = w
        self.root.update_size()

        try: self.stdscr.resize(self.h, self.w)
        except curses.error: pass

        self.on_resize()

    # --------------------------------------------------------------------------
    def _internal_on_update(self) -> None:
        self.on_update()
        self._draw()

        self.char = self.stdscr.getch() # implicitly calls self.stdscr.refresh()
        if self.should_stop(): self.stop()
        self._wait()

    # --------------------------------------------------------------------------
    def _internal_on_end(self) -> None:
        self.on_end()


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _draw(self) -> None:
        aggregate_layer = prisma.Layer(self.h, self.w)
        for y,x,layer in self.root.compose():
            aggregate_layer.add_layer(y, x, layer)

        idx = 0
        for chars,attr in aggregate_layer.get_strs():
            y,x = divmod(idx, self.w)
            try: self.stdscr.addstr(y, x, chars, attr)
            except curses.error: pass # ignore out of bounds error
            idx += len(chars)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self, fps: int = 0) -> None:
        self.set_fps(fps)
        try:
            self.stdscr = curses.initscr()
            curses.noecho(); curses.cbreak()
            self.stdscr.keypad(1)

            try: curses.start_color()
            except: pass

            self._internal_on_start()
            while self._running:
                self.root.clear()
                self._internal_on_resize()
                self._internal_on_update()
            self._internal_on_end()

        finally:
            if "stdscr" not in self.__dict__: return
            self.stdscr.keypad(0)
            curses.echo(); curses.nocbreak()
            curses.endwin()

    # --------------------------------------------------------------------------
    def stop(self) -> None:
        self._running = False


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def on_start(self) -> None:
        return # overridden by user

    def on_resize(self) -> None:
        return # overridden by user

    def on_update(self) -> None:
        return # overridden by user

    def on_end(self) -> None:
        return # overridden by user

    def should_stop(self) -> bool:
        return False # overridden by user


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_fps(self, fps: int) -> None:
        if not fps:
            self._no_delay = False
            self._nap_ms = 0
            self._wait = lambda: None
        else:
            self._no_delay = True
            self._nap_ms = int(1000 / fps)
            self._wait = lambda: curses.napms(self._nap_ms)

    # --------------------------------------------------------------------------
    def set_size(self, h: int, w: int) -> None:
        print(f"\x1b[8;{h};{w}t")

    # --------------------------------------------------------------------------
    def add_text(self, *args, **kws) -> None:
        self.root.add_text(*args, **kws)

    def add_matrix(self, *args, **kws) -> None:
        self.root.add_matrix(*args, **kws)

    def add_border(self, *args, **kwds) -> None:
        self.root.add_border(*args, **kwds)


# //////////////////////////////////////////////////////////////////////////////
