import curses

from prisma.matrix import MatrixChars, MatrixAttrs
from prisma.utils import Debug; d = Debug("logs/layer.log")

from typing import TYPE_CHECKING
if TYPE_CHECKING: from section import Section

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, sect: "Section"):
        self.h = sect.h
        self.w = sect.w
        self.sect = sect
        self.consts = sect.consts
        self._mat_chars = MatrixChars(self)
        self._mat_attrs = MatrixAttrs(self)


    # --------------------------------------------------------------------------
    def add_layer(self, y, x, other: "Layer", transparency = None):
        if transparency is None:
            transparency = other.consts.MERGE
        self._stamp(y, x, 
            other._mat_chars._mat, 
            other._mat_attrs._mat, 
            transparency
        )
        return self


    # --------------------------------------------------------------------------
    def fill_row(self, i, char = ' ', attr = curses.A_NORMAL):
        self._mat_chars.fill_row(i, char)
        self._mat_attrs.fill_row(i, attr)

    def fill_matrix(self, char = ' ', attr = curses.A_NORMAL):
        self._mat_chars.fill_matrix(char)
        self._mat_attrs.fill_matrix(attr)


    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self._mat_chars.set_size(h, w)
        self._mat_attrs.set_size(h, w)
        self.h = h; self.w = w


    # --------------------------------------------------------------------------
    def add_block(self, y, x, chars, attrs = None, transparency = None):
        if attrs is None: 
            attrs = [[self.consts.BLANK_ATTR for _ in range(self.w)] for _ in range(self.h)]
        elif isinstance(attrs, int):
            attrs = [[attrs for _ in range(self.w)] for _ in range(self.h)]

        if transparency is None: transparency = self.consts.MERGE
        self._mat_chars.load_block(y, x, chars, transparency)
        self._mat_attrs.load_block(y, x, attrs, transparency)

    def add_text(self, y, x, string, attr = None, transparency = None, cut: dict[str, str] = {}):
        if attr is None: attr = self.consts.BLANK_ATTR
        if transparency is None: transparency = self.consts.MERGE
        rows = str(string).split('\n')
        h = min(len(rows), self.h)
        w = min(max(map(len, rows)), self.w)

        chars = [row.ljust(w)[:w] for row in rows[:h]]
        attrs = [[attr for _ in range(w)] for _ in range(h)]

        if isinstance(y, str):
            match y[0].upper():
                case 'T': yval = 0
                case 'C': yval = (self.h - h) // 2
                case 'B': yval = self.h - h
                case  _ : raise ValueError(f"Invalid y value: '{y}'")
            modifier = y[1:]
            if modifier: yval += int(modifier)
        else: yval = y

        if isinstance(x, str):
            match x[0].upper():
                case 'L': xval = 0
                case 'C': xval = (self.w - w) // 2
                case 'R': xval = self.w - w
                case  _ : raise ValueError(f"Invalid x value: '{y}'")
            modifier = x[1:]
            if modifier: xval += int(modifier)
        else: xval = x

        if (xval >= self.w) or (yval >= self.h): return

        for k,v in cut.items():
            match k.upper():
                case 'T': chars = chars[v:]
                case 'B': chars = chars[:self.h-yval-v]
                case 'L': chars = tuple(map(lambda row: row[v:], chars))
                case 'R': chars = tuple(map(lambda row: row[:self.w-xval-v], chars))
                case  _ : raise ValueError(f"Invalid cut key: '{k}'")

        self._stamp(yval, xval, chars, attrs, transparency)


    # --------------------------------------------------------------------------
    def get_strs(self):

        flat_chars = ''.join(self._mat_chars._mat)
        flat_attrs = [attr for row in self._mat_attrs._mat for attr in row]

        attrs_offset_0 = flat_attrs[:-1]
        attrs_offset_1 = flat_attrs[1:]

        attrs_mask = (a != b for a,b in zip(attrs_offset_0, attrs_offset_1))
        border_idxs = [0] + [i for i,a in enumerate(attrs_mask, start = 1) if a] + [len(flat_chars)]

        for i0,i1 in zip(border_idxs[:-1], border_idxs[1:]):
            yield flat_chars[i0:i1], flat_attrs[i0]


    # --------------------------------------------------------------------------
    def _stamp(self, y, x, chars, attrs, transparency):
        self._mat_chars.stamp(y, x, chars, transparency)
        self._mat_attrs.stamp(y, x, attrs, transparency)


# //////////////////////////////////////////////////////////////////////////////
