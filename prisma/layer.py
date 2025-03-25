import curses
import numpy as np

def overlay(orig, modf):
    return ''.join(m if m != ' ' else o for o,m in zip(orig, modf))


# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, h, w, dtype = bool):
        self.h = h
        self.w = w
        self.arr = np.zeros((h,w), dtype = dtype)

        self._char_map = [' ' for _ in range(8*self.arr.itemsize)]
        self._attr_map = [curses.A_NORMAL for _ in self._char_map]
        self._dtype = self.arr.dtype # ensures _dtype is correct

        self._rows = []
        self._add_rows(self.h)


    # --------------------------------------------------------------------------
    def _add_rows(self, n):
        self._rows += [self.w*' ' for _ in range(n)]

    def _remove_rows(self, n):
        self._rows = self._rows[:n]

    def _add_cols(self, n):
        self._rows = [row + n*' ' for row in self._rows]

    def _remove_cols(self, n):
        self._rows = [row[:n] for row in self._rows]

    # def _overwrite_row(self, data, start, end):
        # pass

    # def _overlay_row(self, data, start, end):
        # pass

    # --------------------------------------------------------------------------
    def _overwrite_block(self, data, start, end):
        y0,x0 = start
        y1,x1 = end
        orig = self._rows[y0,y1]
        modf = data[y0,y1]
        self._rows[y0,y1] = [o[:x0]+m[x0:x1]+o[x1:] for o,m in zip(orig, modf)]

    def _overlay_block(self, data, start, end):
        y0,x0 = start
        y1,x1 = end
        orig = self._rows[y0,y1]
        modf = data[y0,y1]
        self._rows[y0,y1] = [o[:x0]+overlay(m[x0:x1], o[x0:x1])+o[x1:] for o,m in zip(orig, modf)]




    # --------------------------------------------------------------------------
    def _stamp(self, y, x, data, overwrite):
        if (y >= self.h) or (x >= self.w) or not data: return

        h_data = len(data)
        stamped = self._rows[y:y+h_data+1]
        h_stamped = len(stamped)

        w_data = data[0]
        w_stamped = self._rows[0][x:x+w_data+1]

        start = (y, y + h_stamped + 1)
        end   = (x, x + w_stamped + 1)

        f = self._overwrite_block if overwrite else self._overlay_block
        f(data, start, end)


    # --------------------------------------------------------------------------
    def addimg(self, img, y = 0, x = 0):
        arr = np.load(img).astype(self._dtype) \
            if isinstance(img, str) else img

        arr = ~arr # [WIP] fix this

        h,w = arr.shape
        imgh = max(h, self.h)
        imgw = max(w, self.w)
        self.arr[y:y+h, x:x+w] = arr[:imgh, :imgw]

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



    def draw(self):
        w,h = self.arr.shape

        mask_f = self.arr.flatten()
        borders = mask_f.copy()
        borders[1:] ^= mask_f[:-1]
        borders[-1] |= mask_f[-1]
        idxs = np.arange(len(borders))[borders]

        for i0,i1 in zip(idxs[0::2], idxs[1::2]):
            s = (i1-i0)*self._char_map[1] # [TODO] hardcoded
            y,x = divmod(i0, h)
            yield y, x, s, self._attr_map[1]



# //////////////////////////////////////////////////////////////////////////////
