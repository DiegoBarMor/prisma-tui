import curses
import numpy as np

from prisma.matrix import MatrixChars, MatrixAttrs

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, h, w, dtype = bool):
        self.h = h
        self.w = w

        self._mat_chars = MatrixChars(h, w)
        self._mat_attrs = MatrixAttrs(h, w)

        arr = np.empty(0, dtype = dtype)

        n = 8 * arr.itemsize
        self._mat_chars.init_map(n)
        self._mat_attrs.init_map(n)
        self._dtype = arr.dtype # ensures _dtype is correct


    # --------------------------------------------------------------------------
    def __add__(self, other: "Layer"):
        if (self.h != other.h) or (self.w != other.w):
            raise ValueError("Cannot add layers of different sizes")

        self._stamp(0, 0, other._mat_chars._mat, other._mat_attrs._mat, False)
        return self


    # --------------------------------------------------------------------------
    def _stamp(self, y, x, chars, attrs, overwrite):
        self._mat_chars.stamp(y, x, chars, overwrite)
        self._mat_attrs.stamp(y, x, attrs, overwrite)


    # --------------------------------------------------------------------------
    def fill(self, char = ' ', attr = curses.A_NORMAL):
        self._mat_chars.fill(char)
        self._mat_attrs.fill(attr)


    # --------------------------------------------------------------------------
    def set_chattr(self, idx, char = '', attr = curses.A_NORMAL):
        self._mat_chars.set_idx_map(idx, char)
        self._mat_attrs.set_idx_map(idx, attr)


    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        self._mat_chars.set_size(h, w)
        self._mat_attrs.set_size(h, w)
        self.h = h; self.w = w


    # --------------------------------------------------------------------------
    def add_img(self, y, x, img, overwrite = False):
        arr = np.load(img).astype(self._dtype) \
            if isinstance(img, str) else img

        arr = ~arr # [WIP] fix this

        self._mat_chars.load_arr(y, x, arr, overwrite)
        self._mat_attrs.load_arr(y, x, arr, overwrite)


    # --------------------------------------------------------------------------
    def add_text(self, s, y = 0, x = 0, attr = curses.A_NORMAL, overwrite = False, cut: dict[str, str] = {}):
        rows = str(s).split('\n')
        h = len(rows)
        w = max(map(len, rows))

        chars = [row.ljust(w) for row in rows]
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

        self._stamp(yval, xval, chars, attrs, overwrite)


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


# //////////////////////////////////////////////////////////////////////////////
