import curses

# //////////////////////////////////////////////////////////////////////////////
class Matrix:
    BLANK = None

    def __init__(self, h, w):
        self.h = h
        self.w = w
        self._mat = []
        self.value_map = []

    def init_map(self, n):
        self.value_map = [self.BLANK for _ in range(n)]

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
        func = self.overwrite_row if overwrite else self.overlay_row
        modf = data[:y1-y0]
        orig = self._mat[y0:y1]
        self._mat[y0:y1] = [func(o,m,x0,x1) for o,m in zip(orig, modf)]

    def fill(self, val):
        self._mat = [self._new_subrow(self.w, val) for _ in range(self.h)]

    # --------------------------------------------------------------------------
    @classmethod
    def overwrite_row(cls, orig, modf, i0, i1):
        return orig[:i0] + modf[:i1-i0] + orig[i1:]


    # --------------------------------------------------------------------------
    @classmethod
    def overlay_row(cls, orig, modf, i0, i1):
        middle = [
            cls._overlay_val(o,m) for o,m in zip(orig[i0:i1], modf[:i1-i0])
        ]
        if isinstance(orig, str): middle = ''.join(middle)
        return orig[:i0] + middle + orig[i1:]


    # ------------------------------------------------------------------------------


    def _new_subrow(self, length, val = None): pass

    @classmethod
    def _overlay_val(cls, val_orig, val_modf): pass

    def load_arr(self, y, x, arr, overwrite): pass


# //////////////////////////////////////////////////////////////////////////////
class MatrixChars(Matrix):
    BLANK = ' '
    def __init__(self, h, w):
        super().__init__(h, w)
        self.add_rows(h)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.BLANK
        return length * val

    @classmethod
    def _overlay_val(cls, val_orig, val_modf):
        return val_modf if val_modf != cls.BLANK else val_orig

    def load_arr(self, y, x, arr, overwrite):
        data = [''.join(self.value_map[i] for i in row) for row in arr]
        self.stamp(y, x, data, overwrite)


# //////////////////////////////////////////////////////////////////////////////
class MatrixAttrs(Matrix):
    BLANK = curses.A_NORMAL
    def __init__(self, h, w):
        super().__init__(h, w)
        self.add_rows(h)

    def _new_subrow(self, length, val = None):
        if val is None: val = self.BLANK
        return [val for _ in range(length)]

    @classmethod
    def _overlay_val(cls, val_orig, val_modf):
        # return val_modf if val_modf != cls.BLANK else val_orig
        return val_modf | val_orig

    def load_arr(self, y, x, arr, overwrite):
        data = [[self.value_map[i] for i in row] for row in arr]
        self.stamp(y, x, data, overwrite)


# //////////////////////////////////////////////////////////////////////////////
