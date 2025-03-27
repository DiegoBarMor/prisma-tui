import sys
import numpy as np
from PIL import Image
from pathlib import Path

path_img = Path(sys.argv[1])
path_npy = path_img.with_suffix(".npy")

img = Image.open(path_img).convert("RGBA")
arr = np.array(img)
alpha = arr[:, :, 3]

print(alpha.shape)

out = np.zeros_like(alpha)
out[alpha > 128] = 1



np.save(path_npy, out)
