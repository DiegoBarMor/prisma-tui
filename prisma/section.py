import curses
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, window: curses.window):
        self._win = window
        self.y = 0
        self.x = 0

    @classmethod
    def newwin(cls, height, width, y = 0, x = 0):
        return cls(window = curses.newwin(height, width, y, x))

    # --------------------------------------------------------------------------
    def safe_addstr(self, s, attr):
        args = (self.y, self.x, s) if attr is None \
            else (self.y, self.x, s, attr)

        ### ignore out of bounds error
        try: self._win.addstr(*args)
        except curses.error: pass

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
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

    # --------------------------------------------------------------------------
    def erase(self): self._win.erase()
    def draw(self): self._win.refresh()


# //////////////////////////////////////////////////////////////////////////////
