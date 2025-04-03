import prisma

# //////////////////////////////////////////////////////////////////////////////
class Pixel:
    def __init__(self, char = prisma.BLANK_CHAR, attr = prisma.BLANK_ATTR):
        self._char = char
        self._attr = attr

    # --------------------------------------------------------------------------
    def __repr__(self):
        return f"Pixel({self._char}, {self._attr})"

    # --------------------------------------------------------------------------
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
    def __init__(self, h, w):
        self.h = h
        self.w = w
        self._data: list[list[prisma.Pixel]]
        self.reset()

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)


    def reset(self):
        self._data = [self._new_array(self.w) for _ in range(self.h)]

    def set_size(self, h, w):
        if   h < self.h: self._remove_rows(h)
        elif h > self.h: self._add_rows(h - self.h)
        self.h = h

        if   w < self.w: self._remove_cols(w)
        elif w > self.w: self._add_cols(w - self.w)
        self.w = w

    def _add_rows(self, n):
        self._data += [self._new_array(self.w) for _ in range(n)]

    def _add_cols(self, n):
        self._data = [row + self._new_array(n) for row in self._data]

    def _remove_rows(self, n):
        self._data = self._data[:n]

    def _remove_cols(self, n):
        self._data = [row[:n] for row in self._data]

    def _new_array(self, length):
        return [prisma.Pixel() for _ in range(length)]


# //////////////////////////////////////////////////////////////////////////////
