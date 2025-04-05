import prisma

# //////////////////////////////////////////////////////////////////////////////
class Layer:
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self._transparency = True
        self._pixels = prisma.PixelMatrix(h, w)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_size(self, h, w):
        self.h = h
        self.w = w
        self._pixels.set_size(h, w)

    # --------------------------------------------------------------------------
    def set_transparency(self, transparency: bool) -> None:
        self._transparency = transparency

    # --------------------------------------------------------------------------
    def clear(self):
        self._pixels.reset()

    # --------------------------------------------------------------------------
    def merge_layer(self, y: int, x: int, other: "Layer"):
        self._stamp(y, x, other._pixels, other._transparency)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def draw_matrix(self, y, x, matrix: "prisma.PixelMatrix", transparency = True):
        h = min(matrix.h, self.h)
        w = min(matrix.w, self.w)
        matrix.set_size(h, w)
        y, x = self._parse_coords(h, w, y, x)
        self._stamp(y, x, matrix, transparency)

    # --------------------------------------------------------------------------
    def draw_text(self, y, x, string, attr = None, transparency = True, cut: dict[str, str] = {}):
        if attr is None: attr = prisma.BLANK_ATTR

        rows = str(string).split('\n')
        h = min(len(rows), self.h)
        w = min(max(map(len, rows)), self.w)

        chars = [row.ljust(w, prisma.BLANK_CHAR)[:w] for row in rows[:h]]

        y, x = self._parse_coords(h, w, y, x)

        if (x >= self.w) or (y >= self.h): return

        chars = self._parse_cut(y, x, cut, chars)
        attrs = [[attr for _ in row] for row in chars]

        matrix = prisma.PixelMatrix(h, w, chars, attrs)
        self._stamp(y, x, matrix, transparency)

    # --------------------------------------------------------------------------
    def draw_border(self,
        ls = '│', rs = '│', ts = '─', bs = '─',
        tl = '┌', tr = '┐', bl = '└', br = '┘',
        attr = None
    ):
        if attr is None: attr = prisma.BLANK_ATTR

        h = self.h - 2
        w = self.w - 2
        BC = prisma.BLANK_CHAR
        BA = prisma.BLANK_ATTR
        self.draw_matrix(
            0,0, prisma.PixelMatrix(
                self.h, self.w,
                chars = \
                    [tl + ts*w + tr] +\
                    [ls + BC*w + rs]*h +\
                    [bl + bs*w + br],
                attrs = \
                    [[attr] + [attr]*w + [attr]] +\
                    [[attr] + [ BA ]*w + [attr]]*h +\
                    [[attr] + [attr]*w + [attr]]
            )
        )


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def yield_render_data(self):
        flat_chars = ''.join(''.join(pixel._char for pixel in row) for row in self._pixels)
        flat_attrs = [pixel._attr for row in self._pixels for pixel in row]

        attrs_offset_0 = flat_attrs[:-1]
        attrs_offset_1 = flat_attrs[1:]

        attrs_mask = (a != b for a,b in zip(attrs_offset_0, attrs_offset_1))
        border_idxs = [0] + [i for i,a in enumerate(attrs_mask, start = 1) if a] + [len(flat_chars)]

        for i0,i1 in zip(border_idxs[:-1], border_idxs[1:]):
            yield flat_chars[i0:i1], flat_attrs[i0]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _parse_coords(self, h, w, y, x):
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

        return yval, xval


    # --------------------------------------------------------------------------
    def _parse_cut(self, y, x, cut, data):
        for k,v in cut.items():
            match k.upper():
                case 'T': data = data[v:]
                case 'B': data = data[:self.h-y-v]
                case 'L': data = tuple(map(lambda row: row[v:], data))
                case 'R': data = tuple(map(lambda row: row[:self.w-x-v], data))
                case  _ : raise ValueError(f"Invalid cut key: '{k}'")
        return data


    # --------------------------------------------------------------------------
    def _stamp(self, y, x, data, transparency):
        if (y >= self.h) or (x >= self.w): return
        if not len(data): return

        func = prisma.Pixel.overlay if transparency else prisma.Pixel.overwrite

        h = len(data)
        w = len(data[0])

        y0 = y; x0 = x
        y1 = min(y + h, self.h)
        x1 = min(x + w, self.w)

        mat_orig = self._pixels[y0:y1]
        mat_modf = data[:y1-y]

        self._pixels[y0:y1] = [
            row_orig[:x0] + [
                func(o,m) for o,m in zip(row_orig[x0:x1], row_modf[:x1-x])
            ] + row_orig[x1:]
            for row_orig, row_modf in zip(mat_orig, mat_modf)
        ]


# //////////////////////////////////////////////////////////////////////////////
