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
