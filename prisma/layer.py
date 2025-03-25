import curses
import numpy as np

import prisma.utils.funcs_layer as _layer

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, h, w, dtype = bool):
        self.h = h
        self.w = w

        arr = np.empty(0, dtype = dtype)

        self.blank_char = ' '
        self.blank_attr = curses.A_NORMAL

        n = 8 * arr.itemsize
        self._char_map = [self.blank_char for _ in range(n)]
        self._attr_map = [self.blank_attr for _ in range(n)]
        self._dtype = arr.dtype # ensures _dtype is correct

        self._mat_chars = []
        self._mat_attrs = []
        self._add_rows(self.h)


    # --------------------------------------------------------------------------
    def _add_rows(self, n):
        self._mat_chars += [self.w * self.blank_char  for _ in range(n)]
        self._mat_attrs += [[self.blank_attr for _ in range(self.w)] for _ in range(n)]

    def _add_cols(self, n):
        self._mat_chars = [row + n * self.blank_char  for row in self._mat_chars]
        self._mat_attrs = [row + [self.blank_attr for _ in range(n)] for row in self._mat_attrs]

    def _remove_rows(self, n):
        self._mat_chars = self._mat_chars[:n]
        self._mat_attrs = self._mat_attrs[:n]

    def _remove_cols(self, n):
        self._mat_chars = [row[:n] for row in self._mat_chars]
        self._mat_attrs = [row[:n] for row in self._mat_attrs]


    # --------------------------------------------------------------------------
    def _stamp(self, y, x, data, overwrite):
        mat_chars, mat_attrs = data
        if (y >= self.h) or (x >= self.w): return

        h_kernel = len(mat_chars)
        w_kernel = len(mat_chars[0])

        stamped = self._mat_chars[y:y+h_kernel]
        h_stamped = len(stamped)
        w_stamped = len(stamped[0][x:x+w_kernel])

        y0, y1 = (y, y + h_stamped)
        x0, x1 = (x, x + w_stamped)

        func = _layer.overwrite_row if overwrite else _layer.overlay_row

        modf_chars = mat_chars[:h_stamped]
        modf_attrs = mat_attrs[:h_stamped]
        orig_chars = self._mat_chars[y0:y1]
        orig_attrs = self._mat_attrs[y0:y1]
        self._mat_chars[y0:y1] = [func(o,m,x0,x1) for o,m in zip(orig_chars, modf_chars)]
        self._mat_attrs[y0:y1] = [func(o,m,x0,x1) for o,m in zip(orig_attrs, modf_attrs)]


    # --------------------------------------------------------------------------
    def addimg(self, y, x, img, overwrite = False):
        arr = np.load(img).astype(self._dtype) \
            if isinstance(img, str) else img

        arr = ~arr # [WIP] fix this

        data = (_layer.np2str(arr, self._char_map), _layer.np2list(arr, self._attr_map))
        self._stamp(y, x, data, overwrite)


    # --------------------------------------------------------------------------
    def setchattr(self, idx, char = '', attr = curses.A_NORMAL):
        self._char_map[idx] = char
        self._attr_map[idx] = attr


    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w


    # --------------------------------------------------------------------------
    def get_strs(self):
        flat_chars = ''.join(self._mat_chars)
        flat_attrs = [attr for row in self._mat_attrs for attr in row]

        attrs_offset_0 = flat_attrs[:-1]
        attrs_offset_1 = flat_attrs[1:]

        attrs_mask = (a != b for a,b in zip(attrs_offset_0, attrs_offset_1))
        border_idxs = [0] + [i for i,a in enumerate(attrs_mask, start = 1) if a] + [len(flat_chars)]

        for i0,i1 in zip(border_idxs[:-1], border_idxs[1:]):
            yield flat_chars[i0:i1], flat_attrs[i0]


# //////////////////////////////////////////////////////////////////////////////
