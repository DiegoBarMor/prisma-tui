import sys
import numpy as np
from PIL import Image
from pathlib import Path

path_img = Path(sys.argv[1])
path_npy = path_img.with_suffix(".npy")

img = Image.open(path_img)
arr = np.array(img)
np.save(path_npy, arr.astype(bool))
