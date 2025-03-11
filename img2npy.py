import numpy as np
from PIL import Image

img = Image.open("icon.png")
arr = np.array(img)
np.save("icon.npy", arr.astype(bool))
