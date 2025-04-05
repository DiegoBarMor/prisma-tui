import prisma

# //////////////////////////////////////////////////////////////////////////////
class Pixel:
    def __init__(self, char = prisma.BLANK_CHAR, attr = prisma.BLANK_ATTR):
        self._char = char
        self._attr = attr


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def overwrite(self, other: "Pixel") -> "Pixel":
        self._char = other._char
        self._attr = other._attr
        return self

    # --------------------------------------------------------------------------
    def overlay(self, other: "Pixel") -> "Pixel":
        if (other._char != prisma.BLANK_CHAR) or (other._attr != prisma.BLANK_ATTR):
            self._char = other._char
            self._attr = other._attr
        return self


# //////////////////////////////////////////////////////////////////////////////
class PixelMatrix:
    def __init__(self, h, w, chars: list[str] = None, attrs: list[list[int]] = None):
        if chars is None: chars = ((prisma.BLANK_CHAR for _ in range(w)) for _ in range(h))
        if attrs is None: attrs = ((prisma.BLANK_ATTR for _ in range(w)) for _ in range(h))
        self.h = h
        self.w = w
        self._data: list[list[prisma.Pixel]] = [
            [prisma.Pixel(c,a) for c,a in zip(row_chars, row_attrs)]
            for row_chars, row_attrs in zip(chars, attrs)
        ]

    # --------------------------------------------------------------------------
    def __getitem__(self, index):
        return self._data[index]

    # --------------------------------------------------------------------------
    def __setitem__(self, index, value):
        self._data[index] = value

    # --------------------------------------------------------------------------
    def __iter__(self):
        return iter(self._data)

    # --------------------------------------------------------------------------
    def __len__(self):
        return len(self._data)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def reset(self):
        self._data = [self._create_row(self.w) for _ in range(self.h)]

    # --------------------------------------------------------------------------
    def copy(self):
        return PixelMatrix(
            self.h, self.w,
            ((p._char for p in row) for row in self._data),
            ((p._attr for p in row) for row in self._data)
        )

    # --------------------------------------------------------------------------
    def get_chars(self):
        return [[pixel._char for pixel in row] for row in self._data]

    # --------------------------------------------------------------------------
    def get_attrs(self):
        return [[pixel._attr for pixel in row] for row in self._data]

    # --------------------------------------------------------------------------
    def set_size(self, h, w):
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def _create_row(self, length):
        return [prisma.Pixel() for _ in range(length)]

    # --------------------------------------------------------------------------
    def _add_rows(self, n):
        self._data += [self._create_row(self.w) for _ in range(n)]

    # --------------------------------------------------------------------------
    def _add_cols(self, n):
        self._data = [row + self._create_row(n) for row in self._data]

    # --------------------------------------------------------------------------
    def _remove_rows(self, n):
        self._data = self._data[:n]

    # --------------------------------------------------------------------------
    def _remove_cols(self, n):
        self._data = [row[:n] for row in self._data]


# //////////////////////////////////////////////////////////////////////////////
