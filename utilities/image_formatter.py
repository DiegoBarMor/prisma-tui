import prisma
import numpy as np
from PIL import Image
from pathlib import Path
from collections import Counter

# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def open_img(path_img: Path) -> np.array:
    img = Image.open(path_img).convert("RGBA")
    return np.array(img)

# ------------------------------------------------------------------------------
def sep_channels(img: np.array) -> tuple[np.array]:
    rgb = img[:,:,:3]
    alpha = img[:,:,3]
    return rgb2curses(rgb), alpha

# ------------------------------------------------------------------------------
def rgb2curses(rgb):
    return 1000 * rgb.astype(int) / 255


# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def generate_palette(img: np.array) -> np.array:
    curses_colors = [  # default curses colors
        (  0,  0,  0), # 0: curses.COLOR_BLACK
        (680,  0,  0), # 1: curses.COLOR_RED
        (  0,680,  0), # 2: curses.COLOR_GREEN
        (680,680,  0), # 3: curses.COLOR_YELLOW
        (  0,  0,680), # 4: curses.COLOR_BLUE
        (680,  0,680), # 5: curses.COLOR_MAGENTA
        (  0,680,680), # 6: curses.COLOR_CYAN
        (680,680,680), # 7: curses.COLOR_WHITE
    ]

    rgb,alpha = sep_channels(img)
    bg = rgb[alpha >= prisma.ALPHA_THRESHOLD]
    lst_colors = [tuple(color) for color in bg.reshape(-1,3)]

    count = Counter(lst_colors)
    for color in curses_colors:
        count.pop(color, None)

    ### the first 8 colors are normally reserved for curses defaults
    ### they can be overriden them later on in the .pal file if needed
    colors = curses_colors +  [
        t[0] for t in sorted(
            count.items(), key = lambda t: t[1], reverse = True
        )
    ]
    out_colors = colors[:prisma.MAX_PALETTE_COLORS]
    out_pairs = [(0,i) for i in range(len(out_colors))]
    ### ^^^ fg is automatically set to black for all pairs
    ### this can be changed in the .pal file if needed

    print(f"Extracted {len(out_colors)}/{len(colors)} colors into palette")
    return out_colors, out_pairs


# ------------------------------------------------------------------------------
def to_palette_values(img: np.array, palcolors: np.array) -> np.array:
    rgb,alpha = sep_channels(img)
    w, h, _ = rgb.shape # (w,b,3)
    rgb_flat = rgb.reshape(-1, 3) # (w,h,3)->(w*h,3)
    rgb_broad = rgb_flat[:,None,:] # (w*h,3)->(w*h,1,3)
    palette_broad = palcolors[None,:,:] # (p,3)->(1,p,3)
    dists = np.sum((rgb_broad - palette_broad) ** 2, axis = 2) # (w*h,p)
    idxs = np.argmin(dists, axis = 1) # (w*h,)
    idxs = idxs.reshape(w,h) # (w,h)
    idxs[alpha < prisma.ALPHA_THRESHOLD] = 0 # 0 represents transparent pixels

    print(type(rgb))
    print(type(idxs[idxs > 0]))

    unique_colors = set([tuple(color) for color in rgb_flat])
    unique_palvals = set(idxs[idxs > 0].flatten())

    print(f"Converted img from {len(unique_colors)} colors to {len(unique_palvals)} palette values")
    return idxs


################################################################################
if __name__ == "__main__":
    # mode = sys.argv[1]
    # path_img = Path(sys.argv[2])
    path_img = Path("demos/data/cat.png")
    path_pal = Path("demos/data/cat.pal")
    path_pri = path_img.with_suffix(".pri")

    g = prisma.Graphics()
    img = open_img(path_img)

    colors, pairs = generate_palette(img)
    g.set_colors(colors)
    g.set_pairs(pairs)
    g.save_palette(path_pal)

    g.load_palette(path_pal)
    colors = np.array(g.palette["colors"])
    arr = to_palette_values(img, colors)

    chars = np.full_like(arr, ' ', dtype = str)
    chars[arr > 0] = ' '
    chars = [''.join(row) for row in chars]

    prisma.Graphics.save_layer(
        path_img.with_suffix(".pri"),
        chars = chars, pairs = arr
    )


################################################################################
