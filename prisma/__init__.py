BLANK_CHAR = ' '
BLANK_ATTR = 0 # curses.A_NORMAL

MAX_PALETTE_COLORS = 256
MAX_PALETTE_PAIRS  = 256
ALPHA_THRESHOLD = 128

from .graphics import Graphics
from .layer import Layer
from .pixel import Pixel, PixelMatrix
from .section import Section
from .terminal import Terminal
from .utils import Debug
