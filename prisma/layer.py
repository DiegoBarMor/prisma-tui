import curses
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, shape, dtype = bool):
        self.h, self.w = shape
        self.arr    = np.zeros(shape, dtype = dtype)

        self._chars = ['' for _ in range(8*self.arr.itemsize)]
        self._attrs = [curses.A_NORMAL for _ in self._chars]
        self._dtype = self.arr.dtype # ensures _dtype is correct

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
        self._chars[idx] = char
        self._attrs[idx] = attr


# //////////////////////////////////////////////////////////////////////////////
