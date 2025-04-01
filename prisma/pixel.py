import curses
from prisma.utils import Debug; d = Debug("logs/pixel.log")

# //////////////////////////////////////////////////////////////////////////////
class Pixel:
    def __init__(self, char = ' ', attr = curses.A_NORMAL):
        self.BLANK_CHAR = ' '
        self.BLANK_ATTR = curses.A_NORMAL
        self._char = char
        self._attr = attr
        self._modf = False
        
    # --------------------------------------------------------------------------
    def __repr__(self):
        return f"Pixel({self._char}, {self._attr})"

    # --------------------------------------------------------------------------
    def overwrite(self, other: "Pixel"):
        self._char = other._char
        self._attr = other._attr
        self._modf = True
        return self

    # --------------------------------------------------------------------------
    def overlay(self, other):
        if other._char != self.BLANK_CHAR:
            self._char = other._char
            self._modf = True         

        if other._attr != self.BLANK_ATTR:
            self._attr = other._attr
            self._modf = True 

        return self

    # --------------------------------------------------------------------------
    def merge(self, other):
        if other._char != self.BLANK_CHAR:
            self._char = other._char
            self._modf = True         

        if other._attr != self.BLANK_ATTR:
            self._attr |= other._attr
            self._modf  = True 

        return self


# //////////////////////////////////////////////////////////////////////////////
