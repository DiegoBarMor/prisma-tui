import curses

from prisma.pixel import Pixel
from prisma.utils import Debug; d = Debug("logs/layer.log")

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self.BLANK_CHAR = ' '
        self.BLANK_ATTR = curses.A_NORMAL
        self._pixels = [[Pixel() for _ in range(self.w)] for _ in range(self.h)]
        self._transparency = True

    # --------------------------------------------------------------------------
    def set_transparency(self, transparency: bool) -> None:
        self._transparency = transparency

    # --------------------------------------------------------------------------
    def add_layer(self, y: int, x: int, other: "Layer") -> "Layer":
        self._stamp(y, x, other._pixels, other._transparency)
        return self

    # --------------------------------------------------------------------------
    def _new_subrow(self, length, char = ' ', attr = curses.A_NORMAL):
        return [Pixel(char, attr) for _ in range(length)]

    def _new_matrix(self, h, w, char = ' ', attr = curses.A_NORMAL):
        return [self._new_subrow(w, char, attr) for _ in range(h)]

    def fill_row(self, i, char = ' ', attr = curses.A_NORMAL):
        self._pixels[i] = self._new_subrow(self.w, char, attr)

    def fill_matrix(self, char = ' ', attr = curses.A_NORMAL):
        for i in range(self.h): self.fill_row(i, char, attr)

    def _add_rows(self, n):
        self._pixels += [self._new_subrow(self.w) for _ in range(n)]

    def _add_cols(self, n):
        self._pixels = [row + self._new_subrow(n) for row in self._pixels]

    def _remove_rows(self, n):
        self._pixels = self._pixels[:n]

    def _remove_cols(self, n):
        self._pixels = [row[:n] for row in self._pixels]

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w

    # --------------------------------------------------------------------------
    def _pixel_matrix(self, mat_chars, mat_attrs):
        return [[Pixel(c,a) for c,a in zip(row_chars, row_attrs)] for row_chars, row_attrs in zip(mat_chars, mat_attrs)]

    # --------------------------------------------------------------------------
    def add_block(self, y, x, chars, attrs = None, transparency = True):
        if attrs is None: attrs = self.BLANK_ATTR
            
        if isinstance(attrs, int):
            attrs = [[attrs for _ in range(self.w)] for _ in range(self.h)]

        self._stamp(y, x, self._pixel_matrix(chars, attrs), transparency)   

    # --------------------------------------------------------------------------
    def add_text(self, y, x, string, attr = None, transparency = True, cut: dict[str, str] = {}):
        if attr is None: attr = self.BLANK_ATTR

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

        self._stamp(yval, xval, self._pixel_matrix(chars, attrs), transparency)   


    # --------------------------------------------------------------------------
    def get_strs(self):
        flat_chars = ''.join(''.join(pixel._char for pixel in row) for row in self._pixels)
        flat_attrs = [pixel._attr for row in self._pixels for pixel in row]

        attrs_offset_0 = flat_attrs[:-1]
        attrs_offset_1 = flat_attrs[1:]

        attrs_mask = (a != b for a,b in zip(attrs_offset_0, attrs_offset_1))
        border_idxs = [0] + [i for i,a in enumerate(attrs_mask, start = 1) if a] + [len(flat_chars)]

        for i0,i1 in zip(border_idxs[:-1], border_idxs[1:]):
            yield flat_chars[i0:i1], flat_attrs[i0]


    # --------------------------------------------------------------------------
    def _stamp(self, y, x, data, transparency):
        if (y >= self.h) or (x >= self.w): return

        func = Pixel.overlay if transparency else Pixel.overwrite

        y0 = y; x0 = x
        y1 = min(y + len(data)   , self.h)
        x1 = min(x + len(data[0]), self.w)

        mat_orig = self._pixels[y0:y1]
        mat_modf = data[:y1-y0]

        self._pixels[y0:y1] = [
            row_orig[:x0] + [
                func(o,m) for o,m in zip(row_orig[x0:x1], row_modf[:x1-x0])
            ] + row_orig[x1:] 
            for row_orig, row_modf in zip(mat_orig, mat_modf)
        ]


# //////////////////////////////////////////////////////////////////////////////
