import curses
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, window: curses.window, hauto = True, wauto = True):
        self._win = window
        self._hauto = hauto
        self._wauto = wauto
        self._orig_h, self._orig_w = window.getmaxyx()
        self.h = self._orig_h
        self.w = self._orig_w
        self.ystr = 0
        self.xstr = 0
        self.ypos, self.xpos = window.getbegyx()
        

    @classmethod
    def newwin(cls, h = 0, w = 0, y = 0, x = 0):
        hauto = not h
        wauto = not w
        if hauto: h = curses.LINES - y
        if wauto: w = curses.COLS  - x
        win = curses.newwin(h, w, y, x)
        return cls(win, hauto, wauto)

    # --------------------------------------------------------------------------
    def reset(self):
        self.ystr = 0
        self.xstr = 0
        self.adjust_size()
        self.erase()

    # --------------------------------------------------------------------------
    def adjust_size(self):      
        self.h = curses.LINES - self.ypos if self._hauto \
            else min(self._orig_h, curses.LINES)
        self.w = curses.COLS  - self.xpos if self._wauto \
            else min(self._orig_w, curses.COLS)
        self._win.resize(self.h, self.w)

    # --------------------------------------------------------------------------
    def safe_addstr(self, s, attr = curses.A_NORMAL):
        args = (self.ystr, self.xstr, s) if attr is None \
            else (self.ystr, self.xstr, s, attr)

        ### ignore out of bounds error
        try: self._win.addstr(*args)
        except curses.error: pass

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def pystr(self, s, y = None, x = None, attr = curses.A_NORMAL):
        match str(y).upper():
            case None: pass
            case "T"|"TOP":    self.ystr = 0
            case "C"|"CENTER": self.ystr = self.h // 2
            case "B"|"BOTTOM": self.ystr = self.h - 1
            case _:            self.ystr = y

        match str(x).upper():
            case None: pass
            case "L"|"LEFT":   self.xstr = 0
            case "C"|"CENTER": self.xstr = (self.w - len(s)) // 2
            case "R"|"RIGHT":  self.xstr = self.w - len(s)
            case _:            self.xstr = x

        self.safe_addstr(s, attr)

    # -------------------------------------------------------------------------
    def addlayer(self, layer):
        w,h = layer.arr.shape

        mask_f = layer.arr.flatten()
        borders = mask_f.copy()
        borders[1:] ^= mask_f[:-1]
        borders[-1] |= mask_f[-1]
        idxs = np.arange(len(borders))[borders]

        for i0,i1 in zip(idxs[0::2], idxs[1::2]):
            s = (i1-i0)*layer._chars[1] # [TODO] hardcoded
            self.ystr = i0 // h
            self.xstr = i0 % h
            self.safe_addstr(s, layer._attrs[1])

        return layer

    # --------------------------------------------------------------------------
    def erase(self): self._win.erase()
    def draw(self): self._win.refresh()
    def border(self, *args): self._win.border(*args)


# //////////////////////////////////////////////////////////////////////////////
