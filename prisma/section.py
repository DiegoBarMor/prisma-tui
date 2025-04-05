import curses
import prisma
from typing import Generator

# //////////////////////////////////////////////////////////////////////////////
class Section:
    def __init__(self, is_root = False):
        self.hrel: int = 1.0
        self.wrel: int = 1.0
        self.yrel: int = 0
        self.xrel: int = 0

        self._parent = None
        self._children: list[Section] = []
        self._layers = []
        self._is_root = is_root

        self.update_hwyx()
        self.main_layer = prisma.Layer(self.h, self.w)
        self.border_layer = prisma.Layer(self.h, self.w)


    # --------------------------------------------------------------------------
    def set_parent(self, parent: "Section") -> None:
        self._parent = parent
        parent._children.append(self)
        self.update_hwyx()

    def add_child(self,
        hrel: int|float, wrel: int|float,
        yrel: int|float, xrel: int|float
    ) -> "Section":
        child = Section()
        child.hrel = hrel
        child.wrel = wrel
        child.yrel = yrel
        child.xrel = xrel
        child.set_parent(self)
        return child

    def iter_children(self):
        return iter(self._children)

    def iter_layers(self):
        yield self.main_layer
        for layer in self._layers:
            yield layer
        yield self.border_layer


    # --------------------------------------------------------------------------
    def new_layer(self) -> prisma.Layer:
        layer = prisma.Layer(self.h, self.w)
        self._layers.append(layer)
        return layer

    def mosaic(self, layout: str, divider = '\n') -> dict:
        section_dict = {}
        for char, hwyx in prisma.utils.mosaic(layout, divider).items():
            section = self.add_child(*hwyx)
            section_dict[char] = section
        return section_dict


    # --------------------------------------------------------------------------
    def update_hwyx(self) -> None:
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
    def clear(self) -> None:
        for layer in self.iter_layers():
            layer.clear()

        for child in self.iter_children():
            child.clear()


    def compose(self) -> Generator[tuple[int, int, "prisma.Layer"], None, None]:
        for layer in self.iter_layers():
            yield self.y, self.x, layer

        for child in self.iter_children():
            for out in child.compose():
                yield out


    def adjust_size_pos(self) -> None:
        self.update_hwyx()

        for layer in self.iter_layers():
            layer.set_size(self.h, self.w)

        for child in self.iter_children():
            child.adjust_size_pos()


    # --------------------------------------------------------------------------
    def set_size(self, h, w) -> None:
        self.h = h
        self.w = w
        self.adjust_size_pos()

    def get_size(self) -> tuple[int, int]:
        return self.h, self.w

    def get_pos(self) -> tuple[int, int]:
        return self.y, self.x


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def add_text(self, *args, **kwds):
        self.main_layer.add_text(*args, **kwds)

    def add_matrix(self, *args, **kwds):
        self.main_layer.add_matrix(*args, **kwds)


    # --------------------------------------------------------------------------
    def do_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = None, last = True
    ):
        # [TODO] apply the attr
        if attr is None: attr = prisma.BLANK_ATTR

        h = self.h - 2
        w = self.w - 2
        layer = self.border_layer if last else self.main_layer
        layer.add_text(0,0, '\n'.join((
            tl + w*ts + tr,
            *[ls + w*prisma.BLANK_CHAR + rs]*h,
            bl + w*bs + br,
        )))


# //////////////////////////////////////////////////////////////////////////////
