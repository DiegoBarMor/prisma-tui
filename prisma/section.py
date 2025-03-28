import curses
from collections import OrderedDict

from prisma.utils import mosaic as _mosaic
from prisma.layer import Layer
from prisma.utils import Debug; d = Debug("section.log")
import prisma.settings as _glob


# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, h: int, w: int, y: int, x: int):
        # self._hwyx = h,w,y,x
        self.hrel = h
        self.wrel = w
        self.yrel = y
        self.xrel = x
        self.h: int; self.w: int
        self.y: int; self.x: int
        self._children: list[Section] = []
        self._layers = []

        self._parent = None

        self.update_hwyx()


        self._is_root = False
        self._win: curses.window = curses.newwin(self.h, self.w, self.y, self.x)
        
        self.main_layer = Layer(self.h, self.w)
        self.border_layer = Layer(self.h, self.w)

    # --------------------------------------------------------------------------

    @classmethod
    def init_root(cls, stdscr: curses.window):
        root = cls(1.0, 1.0, 0, 0)
        root._is_root = True
        root._win = stdscr
        return root
    
    # --------------------------------------------------------------------------
    def set_parent(self, parent):
        self._parent = parent
        # self.update_hwyx()

    def add_child(self, section: "Section") -> "Section":
        self._children.append(section)
        section.set_parent(self)
        return section

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
            section = Section(*hwyx)
            self.add_child(section)
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

    def draw(self, root: "Section"):
        for layer in self.iter_layers():
            root.main_layer.add_layer(self.y, self.x, layer)

        for child in self.iter_children():
            child.draw(root)

        if not self._is_root: return

        idx = 0
        for chars,attr in self.main_layer.get_strs():
            y,x = divmod(idx, self.w)
            self.safe_addstr(y, x, chars, attr)
            idx += len(chars)


    def adjust_size_pos(self):
        self.update_hwyx()

        try: self._win.resize(self.h, self.w)
        except curses.error: pass

        try: self._win.mvwin(self.y, self.x)
        except curses.error: pass

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



    # --------------------------------------------------------------------------
    def safe_addstr(self, y, x, s, attr = curses.A_NORMAL):
        try: self._win.addstr(y, x, s, attr)
        except curses.error: pass # ignore out of bounds error


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_text(self, *args, **kwds):
        self.main_layer.add_text(*args, **kwds)


    # --------------------------------------------------------------------------
    def do_border(self, last = True):
        layer = self.border_layer if last else self.main_layer

        # [TODO] add more customization capabilities
        ls = '│' # should be curses.ACS_VLINE    # Starting-column side
        rs = '│' # should be curses.ACS_VLINE    # Ending-column side
        ts = '─' # should be curses.ACS_HLINE    # First-line side
        bs = '─' # should be curses.ACS_HLINE    # Last-line side
        tl = '┌' # should be curses.ACS_ULCORNER # Corner of the first line and the starting column
        tr = '┐' # should be curses.ACS_URCORNER # Corner of the first line and the ending column
        bl = '└' # should be curses.ACS_LLCORNER # Corner of the last line and the starting column
        br = '┘' # should be curses.ACS_LRCORNER # Corner of the last line and the ending column

        h = self.h - 2
        w = self.w - 2
        layer.add_text('\n'.join((
            tl + w*ts + tr,
            *[ls + w*_glob.BLANK_CHAR + rs]*h,
            bl + w*bs + br,
        )))


# //////////////////////////////////////////////////////////////////////////////
