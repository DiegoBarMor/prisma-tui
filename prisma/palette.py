import curses

from prisma import utils
from prisma.utils import Debug; d = Debug("logs/image.log")


# //////////////////////////////////////////////////////////////////////////////
class Palette:
    RESERVED_CURSES_COLORS = 8
    #   0: curses.COLOR_BLACK
    #   1: curses.COLOR_RED
    #   2: curses.COLOR_GREEN
    #   3: curses.COLOR_YELLOW
    #   4: curses.COLOR_BLUE
    #   5: curses.COLOR_MAGENTA
    #   6: curses.COLOR_CYAN
    #   7: curses.COLOR_WHITE
    MAX_PALETTE_COLORS = 256 - RESERVED_CURSES_COLORS

    # --------------------------------------------------------------------------
    def __init__(self):
        self.loaded_pairs: dict = {}

    # --------------------------------------------------------------------------
    def load_palette(self, path_palette: str) -> None:
        palette = utils.load_json(path_palette)

        assert len(palette) <= self.MAX_PALETTE_COLORS, \
            f"Palette has {len(palette)} colors, max is {self.MAX_PALETTE_COLORS}."

        for i, rgb in enumerate(palette):
            curses.init_color(self.RESERVED_CURSES_COLORS + i, *utils.rgb2curses(rgb))

    # --------------------------------------------------------------------------
    def load_pri(self, path_pri: str) -> None:
        with open(path_pri, "rb") as file: 
            h = int.from_bytes(file.read(2), byteorder="little")
            w = int.from_bytes(file.read(2), byteorder="little")           
            nchars = h * (w + 1) - 1 # +1 for breaklines (except the last one)

            file.read(1) # skip a breakline character
            chars = file.read(nchars).decode("utf-8")           
            file.read(1) # skip a breakline character
            
            bg = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            fg = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            
        return chars, bg, fg

    # --------------------------------------------------------------------------
    def save_pri(self, 
        path_pri: str, chars: list[str], fg: list[list[int]], bg: list[list[int]]
    ) -> None:
        h = len(chars)
        w = len(chars[0]) if h > 0 else 0
        
        assert all(len(row) == w for row in chars), "All rows in 'chars' must have the same width."
        assert len(fg) == h and len(bg) == h,       "'fg' and 'bg' must have the same height as 'chars'."
        assert all(len(row) == w for row in fg),    "All rows in 'fg' must have the same width as 'chars'."
        assert all(len(row) == w for row in bg),    "All rows in 'bg' must have the same width as 'chars'."

        with open(path_pri, "wb") as file:
            file.write(h.to_bytes(2, byteorder="little"))
            file.write(w.to_bytes(2, byteorder="little"))
            file.write(b'\n')
            file.write('\n'.join(chars).encode("utf-8"))
            file.write(b'\n')
            
            for row in bg: file.write(bytes(int(x) for x in row))
            for row in fg: file.write(bytes(int(x) for x in row))

    # --------------------------------------------------------------------------
    def setup_pri(self, path_pri: str) -> None:
        string, mat_bg, mat_fg = self.load_pri(path_pri)

        chars = string.split('\n')
        attrs = [[0 for _ in row] for row in mat_fg]
        for i,(row_fg,row_bg) in enumerate(zip(mat_fg, mat_bg)):
            for j,pair in enumerate(zip(row_fg,row_bg)):
                idx = self.loaded_pairs.get(pair)
                if idx is None:
                    idx = len(self.loaded_pairs) + 1
                    self.loaded_pairs[pair] = idx
                    curses.init_pair(idx, *pair)
                attrs[i][j] = curses.color_pair(idx)

        return chars, attrs


# //////////////////////////////////////////////////////////////////////////////
