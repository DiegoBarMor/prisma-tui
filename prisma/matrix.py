import curses

import prisma.utils.funcs_layer as _layer

# //////////////////////////////////////////////////////////////////////////////
class Matrix:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self._mat = []
        self.value_map = []
        self.blank = None

    def init_map(self, n):
        self.value_map = [self.blank for _ in range(n)]

    def set_idx_map(self, idx, val):
        self.value_map[idx] = val

    def add_rows(self, n):
        self._mat += [self._new_subrow(self.w) for _ in range(n)]

    def add_cols(self, n):
        self._mat = [row + self._new_subrow(n) for row in self._mat]

    def remove_rows(self, n):
        self._mat = self._mat[:n]

    def remove_cols(self, n):
        self._mat = [row[:n] for row in self._mat]


    def set_size(self, h, w):
        if   h < self.h: self.remove_rows(h)
        elif h > self.h: self.add_rows(h - self.h)
        self.h = h

        if   w < self.w: self.remove_cols(w)
        elif w > self.w: self.add_cols(w - self.w)
        self.w = w


    def stamp(self, y, x, data, overwrite):
        if (y >= self.h) or (x >= self.w): return
        h_kernel = len(data)
        w_kernel = len(data[0])

        idxs = ( # y0, x0, y1, x1
            y, x,
            min(y + h_kernel, self.h),
            min(x + w_kernel, self.w)
        )

        y0, x0, y1, x1 = idxs
        func = _layer.overwrite_row if overwrite else _layer.overlay_row
        modf = data[:y1-y0]
        orig = self._mat[y0:y1]
        self._mat[y0:y1] = [func(o,m,x0,x1) for o,m in zip(orig, modf)]

    def fill(self, val):
        self._mat = [self._new_subrow(self.w, val) for _ in range(self.h)]

    def _new_subrow(self, length, val = None): pass

    def load_arr(self, y, x, arr, overwrite): pass


# //////////////////////////////////////////////////////////////////////////////
class MatrixChars(Matrix):
    def __init__(self, h, w):
        super().__init__(h, w)
        self.blank = ' '
        self.add_rows(h)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.blank
        return length * val

    def load_arr(self, y, x, arr, overwrite):
        data = [''.join(self.value_map[i] for i in row) for row in arr]
        self.stamp(y, x, data, overwrite)


# //////////////////////////////////////////////////////////////////////////////
class MatrixAttrs(Matrix):
    def __init__(self, h, w):
        super().__init__(h, w)
        self.blank = curses.A_NORMAL
        self.add_rows(h)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.blank
        return [val for _ in range(length)]

    def load_arr(self, y, x, arr, overwrite):
        data = [[self.value_map[i] for i in row] for row in arr]
        self.stamp(y, x, data, overwrite)


# //////////////////////////////////////////////////////////////////////////////
