import curses

from prisma import utils
from prisma.utils import Debug; d = Debug("logs/image.log")

# //////////////////////////////////////////////////////////////////////////////
class Image:
    RESERVED_CURSES_COLORS = 8
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
            
            file.read(1) # skip a breakline character
            chars = file.read(h*w).decode("utf-8")           
            file.read(1) # skip a breakline character
            
            bg = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            fg = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            
        # return h, w, chars, bg, fg
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
            
            for row in bg: file.write(bytes(row))
            for row in fg: file.write(bytes(row))

    # --------------------------------------------------------------------------
    def setup_pri(self, path_pri: str) -> None:
        chars, mat_bg, mat_fg = self.load_pri(path_pri)

        for row_bg, row_fg in zip(mat_bg, mat_fg):
            for bg, fg in zip(row_bg, row_fg):
                pair = bg, fg
                idx = self.loaded_pairs.get(pair)
                if idx is None:
                    idx = len(self.loaded_pairs) + 1
                    self.loaded_pairs[pair] = idx
                    curses.init_pair(idx, bg, fg)
        
        mat_attrs = [list(map(lambda c: curses.color_pair(c), row)) for row in mat_fg]
        mat_chars = chars.split('\n')

        d.log(*mat_attrs, sep = '\n')
        d.log(*mat_chars, sep = '\n')

    # for i, bg_fg in enumerate(pairs):
    #     idx = self.loaded_pairs.get(bg_fg)
    #     if idx is None:
    #         idx = len(self.loaded_pairs) + 1

    #     curses.init_pair(i + 1, *bg_fg)
    #     self.loaded_pairs[bg_fg] = i + 1
    #     self.root.set_chattr(i + 1, '#', curses.color_pair(i + 1))


# //////////////////////////////////////////////////////////////////////////////
