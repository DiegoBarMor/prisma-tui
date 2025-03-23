import curses
import numpy as np
from collections import OrderedDict

from prisma.utils.mosaic import mosaic as _mosaic

from prisma.debug import Debug; d = Debug("log.log")


# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, hwyx, name = '', parent = None):
        self._hwyx = hwyx
        self._parent: Section = parent
        self._children: OrderedDict[str, Section] = OrderedDict()

        self.name = name
        self.h: int; self.w: int
        self.y: int; self.x: int
        self.update_hwyx()

        self._win: curses.window = curses.newwin(self.h, self.w, self.y, self.x)

        self.ystr = 0
        self.xstr = 0

    # --------------------------------------------------------------------------
    def __repr__(self):
        return f"<Section '{self.name}'>"

    # --------------------------------------------------------------------------
    def set_parent(self, parent):
        self._parent = parent

    # --------------------------------------------------------------------------
    def add_child(self, section: "Section"):
        self._children[section.name] = section
        section.set_parent(self)
        return section

    # --------------------------------------------------------------------------
    def get_child(self, name):
        return self._children[name]

    # --------------------------------------------------------------------------
    def mosaic(self, layout: str, divider = '\n'):
        data_hwyx = _mosaic(layout, divider)
        for char, hwyx in data_hwyx.items():
            self.add_child(Section(hwyx, name = char))

    # --------------------------------------------------------------------------
    def update_hwyx(self):
        if self._parent is None:
            self.h, self.w = curses.LINES, curses.COLS
            self.y, self.x = 0, 0
            return

        h,w,y,x = self._hwyx

        if isinstance(h, float):
            self.h = round(h * self._parent.h)
        elif isinstance(h, int):
            if h < 0: h += self._parent.h
            self.h = min(h, self._parent.h)

        if isinstance(w, float):
            self.w = round(w * self._parent.w)
        elif isinstance(w, int):
            if w < 0: w += self._parent.w
            self.w = min(w, self._parent.w)

        if isinstance(y, float):
            self.y = self._parent.y + round(y * self._parent.h)
        elif isinstance(y, int):
            if y < 0: y += self._parent.h
            self.y = y + self._parent.y

        if isinstance(x, float):
            self.x = self._parent.x + round(x * self._parent.w)
        elif isinstance(x, int):
            if x < 0: x += self._parent.w
            self.x = x + self._parent.x

        y_outbounds = (self.y + self.h) - (self._parent.y + self._parent.h)
        x_outbounds = (self.x + self.w) - (self._parent.x + self._parent.w)

        if y_outbounds > 0: self.y -= y_outbounds
        if x_outbounds > 0: self.x -= x_outbounds


    # --------------------------------------------------------------------------
    def erase(self):
        self.ystr = 0
        self.xstr = 0

        self._win.erase()
        for child in self._children.values():
            child.erase()

    def draw(self):
        self._win.refresh()
        for child in self._children.values():
            child.draw()

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        raise TypeError("Can only set absolute size with 'set_size' to an instance of RootSection.")

    def get_size(self): return self.h, self.w

    # --------------------------------------------------------------------------
    def adjust_size_pos(self):
        d.log()
        d.log(f"ADJUST {self.name}")
        d.log(f"data: {self._hwyx}")
        d.log(f"0) h={self.h} w={self.w} y={self.y} x={self.x}")
        self.update_hwyx()
        d.log(f"1) h={self.h} w={self.w} y={self.y} x={self.x}")

        # try: self._win.mvwin(self.y, self.x)
        # except curses.error: pass

        self._win.resize(self.h, self.w)
        self._win.mvwin(self.y, self.x)
        for child in self._children.values():
            child.adjust_size_pos()


    # --------------------------------------------------------------------------
    def safe_addstr(self, s, attr = curses.A_NORMAL):
        ### ignore out of bounds error
        try: self._win.addstr(
            self.ystr, self.xstr, s, attr
        )
        except curses.error: pass


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def pystr(self, s, y = 0, x = 0, attr = curses.A_NORMAL):
        rows = s.split('\n')
        h = len(rows)
        w = max(map(len, rows))

        if isinstance(y, str):
            match y.upper():
                case "T"|"TOP":    self.ystr = 0
                case "C"|"CENTER": self.ystr = (self.h - h) // 2
                case "B"|"BOTTOM": self.ystr = self.h - h
                case _:            raise ValueError(f"Invalid y value: '{y}'")
        else: self.ystr = y

        if isinstance(x, str):
            match str(x).upper():
                case "L"|"LEFT":   self.xstr = 0
                case "C"|"CENTER": self.xstr = (self.w - w) // 2
                case "R"|"RIGHT":  self.xstr = self.w - w
                case _:            raise ValueError(f"Invalid x value: '{y}'")
        else: self.xstr = x

        s = f"\n{self.xstr*' '}".join(rows)

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
    def border(self, *args): self._win.border(*args)


# //////////////////////////////////////////////////////////////////////////////
class RootSection(Section):
    def __init__(self, stdscr: curses.window):
        self._win = stdscr

        self.name = "root"
        self.h, self.w = stdscr.getmaxyx()
        self.y, self.x = stdscr.getbegyx()

        self._hwyx = (1.0, 1.0, 0, 0)
        self._parent = None
        self._children: OrderedDict[str, Section] = OrderedDict()

        self.ystr = 0
        self.xstr = 0

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self.h = h
        self.w = w
        self.adjust_size_pos()


# //////////////////////////////////////////////////////////////////////////////
