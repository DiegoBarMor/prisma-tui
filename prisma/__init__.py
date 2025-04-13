from .backend import Backend, CursesBackend

BACKEND: Backend = CursesBackend()
BLANK_CHAR = ' '
BLANK_ATTR = 0 # curses.A_NORMAL

MAX_PALETTE_COLORS = 256
MAX_PALETTE_PAIRS  = 256
ALPHA_THRESHOLD = 128

# --------------------------------------------------------------------------
from .graphics import Graphics
from .layer import Layer
from .pixel import Pixel
from .section import Section
from .terminal import Terminal
from .utils import Debug

# --------------------------------------------------------------------------
def set_backend(backend: str|Backend) -> None:
    global BACKEND

    if isinstance(backend, Backend):
        BACKEND = backend

    elif isinstance(backend, str):
        match backend:
            case "curses": BACKEND = CursesBackend()
            case _: raise ValueError(f"Unknown backend: {backend}")


# --------------------------------------------------------------------------
