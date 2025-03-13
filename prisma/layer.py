import curses
import numpy as np

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, dtype = bool):
        self.arr    = np.zeros((curses.LINES, curses.COLS), dtype = dtype)

        self._chars = ['' for _ in range(8*self.arr.itemsize)]
        self._attrs = [curses.A_NORMAL for _ in self._chars]
        self._dtype = self.arr.dtype # ensures _dtype is correct

    def addimg(self, img, y = 0, x = 0):
        arr = np.load(img).astype(self._dtype) \
            if isinstance(img, str) else img

        h,w = arr.shape
        imgh = max(h, curses.LINES)
        imgw = max(w, curses.COLS)
        self.arr[y:y+h, x:x+w] = arr[:imgh, :imgw]

    def chattr(self, idx, char = '', attr = curses.A_NORMAL):
        self._chars[idx] = char
        self._attrs[idx] = attr


# //////////////////////////////////////////////////////////////////////////////
