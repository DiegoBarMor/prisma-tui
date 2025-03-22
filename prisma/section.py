import curses
import numpy as np

from prisma.utils.mosaic import mosaic as _mosaic

from prisma.debug import Debug; d = Debug("out.log")


# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, hwyx, name = '', parent = None, is_relative = False):
        self._hwyx = hwyx
        self._is_relative = is_relative
        self._parent: Section = parent
        self._children: dict[str, Section] = {}

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
    def add_child(self, name, section: "Section"):
        self._children[name] = section
        section.set_parent(self)
        return section

    # --------------------------------------------------------------------------
    def get_child(self, name):
        return self._children[name]

    # --------------------------------------------------------------------------
    def mosaic(self, layout: str, divider = '\n'):
        data_hwyx = _mosaic(layout, divider)
        for char, hwyx in data_hwyx.items():
            self.add_child(char, Section(hwyx, name = char, is_relative = True))

    # --------------------------------------------------------------------------
    def update_hwyx(self):
        if self._parent is None:
            self.h, self.w = curses.LINES, curses.COLS
            self.y, self.x = 0, 0
            return
            
        if self._is_relative:
            relh, relw, rely, relx = self._hwyx
            self.h = round(relh * self._parent.h)# - 1
            self.w = round(relw * self._parent.w)# - 1
            self.y = round(rely * self._parent.h)
            self.x = round(relx * self._parent.w)
        else:
            self.h, self.w, self.y, self.x = self._hwyx
            self.h = min(self.h, self._parent.h)
            self.w = min(self.w, self._parent.w)


        y_outbounds = (self.y + self.h) - self._parent.h
        x_outbounds = (self.x + self.w) - self._parent.w

        d.log("@", y_outbounds)

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
        d.log(f"ADJUST {self.name} (parent {self._parent})")
        d.log(f"0) y={self.y} x={self.x} h={self.h} w={self.w}")
        self.update_hwyx()
        d.log(f"1) y={self.y} x={self.x} h={self.h} w={self.w}")

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
    def border(self, *args): self._win.border(*args)


# //////////////////////////////////////////////////////////////////////////////
class RootSection(Section):
    def __init__(self, stdscr: curses.window):
        self._win = stdscr

        self.name = "root"
        self.h, self.w = stdscr.getmaxyx()
        self.y, self.x = stdscr.getbegyx()

        self._parent = None
        self._children = {}

        self.ystr = 0
        self.xstr = 0

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self.h = h
        self.w = w
        self.adjust_size_pos()


# //////////////////////////////////////////////////////////////////////////////
