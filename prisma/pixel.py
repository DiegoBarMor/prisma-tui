import curses
from prisma.utils import Debug; d = Debug("logs/pixel.log")

# //////////////////////////////////////////////////////////////////////////////
class Pixel:
    def __init__(self, char = ' ', attr = curses.A_NORMAL):
        self.BLANK_CHAR = ' '
        self.BLANK_ATTR = curses.A_NORMAL
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
        if (other._char != self.BLANK_CHAR) or (other._attr != self.BLANK_ATTR):
            self._char = other._char
            self._attr = other._attr
        return self


# //////////////////////////////////////////////////////////////////////////////
