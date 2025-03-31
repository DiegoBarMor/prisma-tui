import json

def hex2rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], base = 16) for i in (0, 2, 4))

def rgb_curses(rgb):
    return tuple(int(1000 * c / 255) for c in rgb)

def merge_colors(r,g,b):
    return r[0], g[1], b[2]

hex_colors = dict( # https://en.wikipedia.org/wiki/List_of_software_palettes#6-8-5_levels_RGB
    reds   = ["#000000", "#330000", "#660000", "#990000", "#CC0000", "#FF0000"],
    greens = ["#000000", "#002400", "#004900", "#006D00", "#009200", "#00B600", "#00DB00", "#00FF00"],
    blues  = ["#000000", "#000040", "#000080", "#0000BF", "#0000FF"],
)

rgb_colors = {k: [rgb_curses(hex2rgb(c)) for c in v] for k,v in hex_colors.items()}

palette = [merge_colors(r,g,b) for r in rgb_colors["reds"] for g in rgb_colors["greens"] for b in rgb_colors["blues"]]

print(palette)

path_palette = "tests/palette.pal"
with open(path_palette, 'w') as file:
    json.dump(palette, file)
