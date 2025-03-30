import sys
import json
import numpy as np
from PIL import Image
from pathlib import Path
from collections import Counter

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.palette import Palette


def open_img(path_img: Path) -> np.array:
    img = Image.open(path_img).convert("RGBA")
    return np.array(img)

def load_palette(path_json: Path) -> np.array:
    with open(path_json, 'r') as file:
        return np.array(json.load(file))

def write_palette(path_json: Path, palette: np.array) -> None:
    with open(path_json, 'w') as file:
        json.dump(
            [color.tolist() for color in palette], file
        )
    

def sep_channels(img: np.array) -> tuple[np.array]:
    rgb = img[:,:,:3]
    alpha = img[:,:,3]
    return rgb, alpha

def n_unique(arr: np.array) -> int:
    return len(set(arr.flatten()))

def colors2strings(arr: np.array) -> np.array:
    return np.array([f"{r},{g},{b}" for r,g,b in arr.reshape(-1,3)], dtype = str)

def strings2colors(strs: list[str]) -> np.array:
    return np.array([s.split(',') for s in strs], dtype = int)

def save_npy(path_npy: Path, img: np.array) -> None:
    np.save(path_npy, img)


def to_palette_values(img: np.array, palette: np.array) -> np.array:
    rgb,alpha = sep_channels(img)
    # print(rgb.shape, alpha.shape)
    # print(palette.shape)

    w, h, _ = rgb.shape # (w,b,3)
    rgb_flat = rgb.reshape(-1, 3) # (w,h,3)->(w*h,3)
    rgb_broad = rgb_flat[:,None,:] # (w*h,3)->(w*h,1,3)
    palette_broad = palette[None,:,:] # (p,3)->(1,p,3)
    dists = np.sum((rgb_broad - palette_broad) ** 2, axis = 2) # (w*h,p)
    idxs = np.argmin(dists, axis = 1) # (w*h,)
    idxs = idxs.reshape(w,h) # (w,h)
    idxs += 8 # first 8 color indicies are reaerved for curses defaults


    idxs[alpha < 128] = 0 # 0 represents transparent pixels

    print(f"Converted img from {n_unique(colors2strings(rgb))} colors to {n_unique(idxs[idxs > 0])} palette values")   
    return idxs 
    

def generate_palette(img: np.array) -> np.array:
    rgb,alpha = sep_channels(img)
    rgb = rgb[alpha >= 128]
    print(rgb)
    print(colors2strings(rgb))
    c = Counter(colors2strings(rgb))
    colors = [t[0] for t in sorted(c.items(), key = lambda t: t[1], reverse = True)]

    
    palette = strings2colors(colors)[:248]
    print(f"Extracted {len(palette)}/{len(colors)} colors into palette")   
    return palette
    

# mode = sys.argv[1]
# path_img = Path(sys.argv[2])
path_img = Path("demos/data/cat.png")
path_palette = "demos/data/cat.json"
path_pri = path_img.with_suffix(".pri")

img = open_img(path_img)

print(img)
print(img.shape)

pal = generate_palette(img)
write_palette(path_palette, pal)

pal = load_palette(path_palette) 
arr = to_palette_values(img, pal)

chars = np.zeros_like(arr, dtype = str)
chars[arr > 0] = '.'
chars[arr == 0] = ' '
chars = [''.join(row) for row in chars]
print(*chars, sep= '\n')
# print(arr)
print(f"  fg:\n{'\n'.join(' '.join(f'{x:2}' for x in row) for row in arr)}")


Palette().save_pri(
    path_img.with_suffix(".pri"),
    chars = chars,
    fg = np.full_like(arr, 0),
    bg = arr
)
