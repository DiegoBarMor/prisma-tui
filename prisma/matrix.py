from abc import ABC, abstractmethod

import prisma.settings as _glob
from prisma.utils import Debug; d = Debug("matrix.log")

# //////////////////////////////////////////////////////////////////////////////
class Matrix(ABC):
    BLANK = None
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self._mat = []
        self._value_lookup = [self.BLANK for _ in range(_glob.LENGHT_VALUE_LOOKUP)]

    # --------------------------------------------------------------------------
    def set_lookup_value(self, idx, val):
        self._value_lookup[idx] = val

    def set_size(self, h, w):
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w


    # --------------------------------------------------------------------------
    def fill_row(self, i, val):
        self._mat[i] = self._new_subrow(self.w, val)

    def fill_matrix(self, val):
        for i in range(self.h): self.fill_row(i, val)


    # --------------------------------------------------------------------------
    def stamp(self, y, x, data, transparency):
        if (y >= self.h) or (x >= self.w): return

        match transparency:
            case _glob.MERGE:     func = self._merge_row
            case _glob.OVERLAY:   func = self._overlay_row
            case _glob.OVERWRITE: func = self._overwrite_row
            case _: raise ValueError()

        y0 = y; x0 = x
        y1 = min(y + len(data)   , self.h)
        x1 = min(x + len(data[0]), self.w)

        orig = self._mat[y0:y1]
        modf = data[:y1-y0]
        self._mat[y0:y1] = [func(o,m,x0,x1) for o,m in zip(orig, modf)]


    # --------------------------------------------------------------------------
    def _add_rows(self, n):
        self._mat += [self._new_subrow(self.w) for _ in range(n)]

    def _add_cols(self, n):
        self._mat = [row + self._new_subrow(n) for row in self._mat]

    def _remove_rows(self, n):
        self._mat = self._mat[:n]

    def _remove_cols(self, n):
        self._mat = [row[:n] for row in self._mat]


    # --------------------------------------------------------------------------
    def _overwrite_row(self, orig, modf, i0, i1):
        return orig[:i0] + modf[:i1-i0] + orig[i1:]

    def _overlay_row(self, orig, modf, i0, i1):
        middle = [
            m if m != self.BLANK else o \
            for o,m in zip(orig[i0:i1], modf[:i1-i0])
        ]
        if isinstance(orig, str): middle = ''.join(middle)
        return orig[:i0] + middle + orig[i1:]


    # ------------------------------------------------------------------------------
    @abstractmethod
    def _new_subrow(self, length, val = None):
        return

    @abstractmethod
    def _merge_row(self, orig, modf, i0, i1):
        return

    @abstractmethod
    def load_block(self, y, x, arr, transparency):
        return


# //////////////////////////////////////////////////////////////////////////////
class MatrixChars(Matrix):
    BLANK = _glob.BLANK_CHAR
    def __init__(self, h, w):
        super().__init__(h, w)
        self._add_rows(h)

    # ------------------------------------------------------------------------------
    def load_block(self, y, x, arr, transparency):
        data = [''.join(self._value_lookup[i] for i in row) for row in arr]
        self.stamp(y, x, data, transparency)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.BLANK
        return length * val

    def _merge_row(self, orig, modf, i0, i1):
        return self._overlay_row(orig, modf, i0, i1)


# //////////////////////////////////////////////////////////////////////////////
class MatrixAttrs(Matrix):
    BLANK = _glob.BLANK_ATTR
    def __init__(self, h, w):
        super().__init__(h, w)
        self._add_rows(h)

    # ------------------------------------------------------------------------------
    def load_block(self, y, x, arr, transparency):
        data = [[self._value_lookup[i] for i in row] for row in arr]
        self.stamp(y, x, data, transparency)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.BLANK
        return [val for _ in range(length)]

    def _merge_row(self, orig, modf, i0, i1):
        middle = [
            o|m for o,m in zip(orig[i0:i1], modf[:i1-i0])
        ]
        return orig[:i0] + middle + orig[i1:]


# //////////////////////////////////////////////////////////////////////////////
