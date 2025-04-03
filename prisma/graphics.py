import curses
import prisma

# //////////////////////////////////////////////////////////////////////////////
class Graphics:

    # --------------------------------------------------------------------------
    def __init__(self):
        self.palette: dict = {"colors": [], "pairs":  []}


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def set_palette_colors(self, colors) -> None:
        self.palette["colors"] = [[int(c) for c in color] for color in colors]

    def set_palette_pairs(self, pairs) -> None:
        self.palette["pairs"] = [[int(p) for p in pair] for pair in pairs]


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def write_palette(self, path_pal: str) -> None:
        prisma.utils.write_json(path_pal, self.palette)

    # --------------------------------------------------------------------------
    def load_palette(self, path_pal: str) -> None:
        self.palette = prisma.utils.load_json(path_pal)
        colors = self.palette["colors"]
        pairs  = self.palette["pairs"]

        assert len(colors) <= prisma.MAX_PALETTE_COLORS, \
            f"Graphics has {len(colors)} colors, max is {prisma.MAX_PALETTE_COLORS}."

        assert len(pairs) <= prisma.MAX_PALETTE_PAIRS, \
            f"Graphics has {len(pairs)} pairs, max is {prisma.MAX_PALETTE_PAIRS}."

        try:
            if not curses.can_change_color(): return
        except curses.error: return

        for i,color in enumerate(colors):
            curses.init_color(i, *color)

        for i,(fg,bg) in enumerate(pairs):
            if not i: continue # first pair is reserved by curses
            curses.init_pair(i, fg, bg)


    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    @classmethod
    def save_pri(cls, path_pri: str, chars: list[str], pairs: list[list[int]]) -> None:
        h = len(chars)
        w = len(chars[0]) if h > 0 else 0

        assert all(len(row) == w for row in chars), "All rows in 'chars' must have the same width."
        assert all(len(row) == w for row in pairs), "All rows in 'pairs' must have the same width as 'chars'."
        assert len(pairs) == h , "'pairs' must have the same height as 'chars'."

        with open(path_pri, "wb") as file:
            file.write(h.to_bytes(2, byteorder="little"))
            file.write(w.to_bytes(2, byteorder="little"))
            file.write(b'\n')
            file.write('\n'.join(chars).encode("utf-8"))
            file.write(b'\n')
            for row in pairs: file.write(bytes(int(x) for x in row))

    # --------------------------------------------------------------------------
    @classmethod
    def load_pri(cls, path_pri: str) -> tuple[list[str], list[list[int]]]:
        with open(path_pri, "rb") as file:
            h = int.from_bytes(file.read(2), byteorder="little")
            w = int.from_bytes(file.read(2), byteorder="little")
            nchars = h * (w + 1) - 1 # +1 for breaklines (except the last one)

            file.read(1) # skip a breakline character
            chars = file.read(nchars).decode("utf-8")
            file.read(1) # skip a breakline character

            pairs = [[int(file.read(1)[0]) for _ in range(w)] for _ in range(h)]
            attrs = [[curses.color_pair(i) for i in row] for row in pairs]
        return chars.split('\n'), attrs


# //////////////////////////////////////////////////////////////////////////////
