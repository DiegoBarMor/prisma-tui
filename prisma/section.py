import curses
from collections import OrderedDict

from prisma.utils.mosaic import mosaic as _mosaic
from prisma.layer import Layer

from prisma.debug import Debug; d = Debug("section.log")


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

        self._layers = [Layer(self.h, self.w)]

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
    def iter_children(self):
        for child in self._children.items():
            yield child

    # --------------------------------------------------------------------------
    def mosaic(self, layout: str, divider = '\n'):
        data_hwyx = _mosaic(layout, divider)
        for char, hwyx in data_hwyx.items():
            self.add_child(Section(hwyx, name = char))

    # --------------------------------------------------------------------------
    def new_layer(self):
        layer = Layer(self.h, self.w)
        self._layers.append(layer)
        return layer

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
    def clear(self):
        for layer in self._layers:
            layer.fill()

        for child in self._children.values():
            child.clear()

    def draw(self):
        layer = Layer(self.h, self.w)
        for next_layer in self._layers:
            layer += next_layer

        idx = 0
        for chars,attr in layer.get_strs():
            y,x = divmod(idx, self.w)
            self.safe_addstr(y, x, chars, attr)
            idx += len(chars)

        self._win.refresh()
        for child in self._children.values():
            child.draw()

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        raise TypeError("Can only set absolute size with 'set_size' to an instance of RootSection.")

    def get_size(self): return self.h, self.w

    # --------------------------------------------------------------------------
    def adjust_size_pos(self):
        self.update_hwyx()

        try: self._win.resize(self.h, self.w)
        except curses.error: pass

        try: self._win.mvwin(self.y, self.x)
        except curses.error: pass

        for layer in self._layers:
            layer.set_size(self.h, self.w)

        for child in self._children.values():
            child.adjust_size_pos()


    # --------------------------------------------------------------------------
    def safe_addstr(self, y, x, s, attr = curses.A_NORMAL):
        try: self._win.addstr(y, x, s, attr)
        except curses.error: pass # ignore out of bounds error


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_text(self, *args, **kwds):
        self._layers[0].add_text(*args, **kwds)


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
        self._layers = [Layer(self.h, self.w)]

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self.h = h
        self.w = w
        self.adjust_size_pos()


# //////////////////////////////////////////////////////////////////////////////
