import sys
import json
import numpy as np
from PIL import Image as PILImage
from pathlib import Path
from collections import Counter

import os, sys; sys.path.insert(0, os.getcwd()) # allow imports from root folder
from prisma.image import Image as PrismaImage


def open_img(path_img: Path) -> np.array:
    img = PILImage.open(path_img).convert("RGBA")
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
    # s = arr.astype("<U3")
    # comma = np.full(arr.shape[:-1], ',', dtype = "<U3")
    # print(s.dtype, comma.dtype)
    # return (s[..., 0] + comma + s[..., 1] + comma + s[..., 2]).astype("<U11")

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

    # x = rgb.astype(str)
    # x = x[:,:,0]+','+x[:,:,1]+','+x[:,:,2]
    # x = x[x != "0,0,0"]
    # print(x.flatten())
    
    print(f"Converted img from {n_unique(colors2strings(rgb))} colors to {n_unique(idxs[idxs > 0])} palette values")   
    return idxs 
    

def generate_palette(img: np.array) -> np.array:
    rgb,alpha = sep_channels(img)
    rgb = rgb[alpha >= 128]
    print(rgb)
    print(colors2strings(rgb))
    c = Counter(colors2strings(rgb))
    colors = [t[0] for t in sorted(c.items(), key = lambda t: t[1], reverse = True)]


    
    # palette = np.array((248,3), dtype = int)
    palette = strings2colors(colors)[:248]
    print(f"Extracted {len(palette)}/{len(colors)} colors into palette")   
    # print(rgb.shape, rgb)
    # print(c)
    # print(len(c))
    # print(*colors, sep='\n')
    # print(palette)
    return palette
    

mode = sys.argv[1]
path_img = Path(sys.argv[2])
path_palette = "tests/cat.json"
path_pri = path_img.with_suffix(".pri")

img = open_img(path_img)

print(img)
print(img.shape)

pal = generate_palette(img)
write_palette(path_palette, pal)

pal = load_palette(path_palette) 
arr = to_palette_values(img, pal)

chars = np.zeros_like(arr, dtype = str)
chars[arr > 0] = '*'
chars[arr == 0] = ' '
chars = [''.join(row) for row in chars]
print(chars)
print(arr)

PrismaImage().save_pri(
    path_img.with_suffix(".pri"),
    chars = chars,
    fg = np.zeros_like(arr),
    bg = arr
)

# save_npy(path_npy, npy)

# save_npy(path_img, alpha > 128)

# print(rgb)


# palette += 8 

# print(palette)
