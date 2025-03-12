import curses
import numpy as np
from collections.abc import Callable

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, dtype = bool):
        self.arr    = np.zeros((curses.LINES, curses.COLS), dtype = dtype)
        
        self._chars = ['' for _ in range(8*self.arr.itemsize)]
        self._attrs = [curses.A_NORMAL for _ in self._chars]
        self._dtype = self.arr.dtype # ensures _dtype is correct

    def addimg(self, img, y = 0, x = 0):       
        arr = np.load(img).astype(self._dtype) \
            if isinstance(img, str) else img
    
        h,w = arr.shape
        imgh = max(h, curses.LINES)
        imgw = max(w, curses.COLS)
        # imgh = min(h, curses.LINES)
        # imgw = min(w, curses.COLS)
        self.arr[y:y+h, x:x+w] = arr[:imgh, :imgw]

    def chattr(self, idx, char = '', attr = curses.A_NORMAL):
        self._chars[idx] = char
        self._attrs[idx] = attr


# //////////////////////////////////////////////////////////////////////////////
class Prisma:
    def __init__(self, fps = None, ignore_outbounds = True):
        self._no_delay: bool
        self._nap_ms: int
        self._wait: Callable
        self.set_fps(fps)

        self._ignore_outbounds = ignore_outbounds
        self._running = False
        # self._wins = []
        self.char = None
        self.y = 0
        self.x = 0

    # --------------------------------------------------------------------------
    def on_init(self):
        return # override!

    def on_update(self):
        return # override!

    def on_end(self):
        return # override!

    def kill_when(self):
        return True # override!

    def wait(self):
        curses.napm(self._nap_ms)

    def kill(self):
        self._running = False

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def run(self):
        try:
            self.stdscr = curses.initscr()
            # self._wins.append(self.stdscr)
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
            # map(lambda win: win.erase(), self._wins)
            self.stdscr.erase()
            self.on_update()
            # map(lambda win: win.refresh(), self._wins)
            self.stdscr.refresh()
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
            self._wait = self.wait

    # --------------------------------------------------------------------------
    # def newwin(self, y, x):
        # win = curses.newwin(y, x)
        # self._wins.append(win)
        # return win
    
    # --------------------------------------------------------------------------
    def safe_addstr(self, s, attr):
        args = lambda: (self.y, self.x, s) if attr is None \
            else (self.y, self.x, s, attr)

        if self._ignore_outbounds:
            try: self.stdscr.addstr(*args())
            except curses.error: pass
        else:
            if align == self.MASK_BOTTOM_RIGHT: self.x -= 1
            self.stdscr.addstr(*args())

    # --------------------------------------------------------------------------
    def pystr(self, s, y = None, x = None, attr = curses.A_NORMAL):
        match str(y).upper():
            case None: pass
            case "T"|"TOP":    self.y = 0
            case "C"|"CENTER": self.y = curses.LINES // 2
            case "B"|"BOTTOM": self.y = curses.LINES - 1
            case _:            self.y = y

        match str(x).upper():
            case None: pass
            case "L"|"LEFT":   self.x = 0
            case "C"|"CENTER": self.x = (curses.COLS - len(s)) // 2
            case "R"|"RIGHT":  self.x = curses.COLS - len(s)
            case _:            self.x = x

        self.safe_addstr(s, attr)

    # --------------------------------------------------------------------------
    def addlayer(self, layer):
        w,h = layer.arr.shape

        mask_f = layer.arr.flatten()
        borders = mask_f.copy()
        borders[1:] ^= mask_f[:-1]
        borders[-1] |= mask_f[-1]
        idxs = np.arange(len(borders))[borders]

        for i0,i1 in zip(idxs[0::2], idxs[1::2]):
            s = (i1-i0)*layer._chars[1] # [TODO] hardcoded
            self.y = i0 // h
            self.x = i0 % h
            self.safe_addstr(s, layer._attrs[1])


# //////////////////////////////////////////////////////////////////////////////
