import curses
from collections import OrderedDict

from prisma.utils import mosaic as _mosaic
from prisma.layer import Layer
from prisma.utils import Debug; d = Debug("logs/section.log")
import prisma.settings as _glob

from typing import TYPE_CHECKING
if TYPE_CHECKING: from terminal import Terminal

# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, term: "Terminal", is_root = False):
    # def __init__(self, h: int, w: int, y: int, x: int, term: "Terminal" = None):
        # self._hwyx = h,w,y,x
        self.hrel: int = 1.0
        self.wrel: int = 1.0
        self.yrel: int = 0
        self.xrel: int = 0

        self._parent = None
        self._children: list[Section] = []
        self._layers = []
        self._term: Terminal = term


        self._is_root = False
        
        # self.h, self.w = curses.LINES, curses.COLS
        # self.y, self.x = 0, 0
        
        self.update_hwyx()

        self.main_layer = Layer(self.h, self.w)
        self.border_layer = Layer(self.h, self.w)


    # --------------------------------------------------------------------------
    def set_parent(self, parent: "Section") -> None:
        self._parent = parent
        parent._children.append(self)
        self.update_hwyx()

    def add_child(self, h: int, w: int, y: int, x: int) -> "Section":
        child = Section(self._term)
        child.hrel = h
        child.wrel = w
        child.yrel = y
        child.xrel = x
        child.set_parent(self)
        return child

    def iter_children(self):
        for child in self._children:
            yield child

    def iter_layers(self):
        yield self.main_layer
        for layer in self._layers:
            yield layer
        yield self.border_layer


    # --------------------------------------------------------------------------
    def new_layer(self) -> Layer:
        layer = Layer(self.h, self.w)
        self._layers.append(layer)
        return layer

    def mosaic(self, layout: str, divider = '\n'):
        section_dict = {}
        for char, hwyx in _mosaic(layout, divider).items():
            section = self.add_child(*hwyx)
            section_dict[char] = section
        return section_dict


    # --------------------------------------------------------------------------
    def update_hwyx(self):
        if self._parent is None:
            self.h, self.w = curses.LINES, curses.COLS
            self.y, self.x = 0, 0
            return

        h = self.hrel
        w = self.wrel
        y = self.yrel
        x = self.xrel

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
        for layer in self.iter_layers():
            layer.fill_matrix()

        for child in self.iter_children():
            child.clear()

    def draw(self):
        for layer in self.iter_layers():
            self._term.root.main_layer.add_layer(self.y, self.x, layer)

        for child in self.iter_children():
            child.draw()

        # if not self._is_root: return

        # idx = 0
        # for chars,attr in self.main_layer.get_strs():
        #     y,x = divmod(idx, self.w)
        #     self.safe_addstr(y, x, chars, attr)
        #     idx += len(chars)


    def adjust_size_pos(self):
        self.update_hwyx()

        # try: self._win.resize(self.h, self.w)
        # except curses.error: pass

        # try: self._win.mvwin(self.y, self.x)
        # except curses.error: pass

        for layer in self.iter_layers():
            layer.set_size(self.h, self.w)

        for child in self.iter_children():
            child.adjust_size_pos()


    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self.h = h
        self.w = w
        self.adjust_size_pos()

    def get_size(self):
        return self.h, self.w

    def get_pos(self):
        return self.y, self.x


    # --------------------------------------------------------------------------
    # def safe_addstr(self, y, x, s, attr = curses.A_NORMAL):
    #     try: self._win.addstr(y, x, s, attr)
    #     except curses.error: pass # ignore out of bounds error


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_text(self, *args, **kwds):
        self.main_layer.add_text(*args, **kwds)


    # --------------------------------------------------------------------------
    def do_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = _glob.BLANK_ATTR, last = True
    ):
        # [TODO] apply the attr

        h = self.h - 2
        w = self.w - 2
        layer = self.border_layer if last else self.main_layer
        layer.add_text(0,0, '\n'.join((
            tl + w*ts + tr,
            *[ls + w*_glob.BLANK_CHAR + rs]*h,
            bl + w*bs + br,
        )))


# //////////////////////////////////////////////////////////////////////////////
