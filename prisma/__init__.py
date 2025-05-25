from .backend import Backend, CursesBackend

_BACKEND: Backend = CursesBackend()
BLANK_CHAR = ' '
BLANK_ATTR = 0 # curses.A_NORMAL

MAX_PALETTE_COLORS = 256
MAX_PALETTE_PAIRS  = 256
ALPHA_THRESHOLD = 128

# --------------------------------------------------------------------------
from .constants import *
from .graphics import Graphics
from .layer import Layer, BlendMode
from .pixel import Pixel
from .section import Section
from .terminal import Terminal
from .utils import Debug

# --------------------------------------------------------------------------
def set_backend(backend: str|Backend) -> None:
    global _BACKEND

    if isinstance(backend, Backend):
        _BACKEND = backend

    elif isinstance(backend, str):
        match backend:
            case "curses": _BACKEND = CursesBackend()
            case _: raise ValueError(f"Unknown backend: {backend}")


# --------------------------------------------------------------------------
def set_nodelay(boolean: bool) -> None:
    """Set the nodelay mode for the backend."""
    _BACKEND.set_nodelay(boolean)

def sleep(ms: int) -> None:
    """Sleep for a given number of milliseconds."""
    _BACKEND.sleep(ms)

def write_text(y: int, x: int, chars: str, attr: int = BLANK_ATTR) -> None:
    """Write text to the terminal at a specific position."""
    _BACKEND.write_text(y, x, chars, attr)

def get_size(update: bool = False) -> tuple[int, int]:
    """Get the size of the terminal."""
    return _BACKEND.get_size(update)

def supports_color() -> bool:
    """Check if the backend supports color."""
    return _BACKEND.supports_color()

def init_color(i: int, r: int, g: int, b: int) -> None:
    """Initialize a color in the terminal."""
    _BACKEND.init_color(i, r, g, b)

def init_pair(i: int, fg: int, bg: int) -> None:
    """Initialize a color pair in the terminal."""
    _BACKEND.init_pair(i, fg, bg)

def get_color_pair(i: int) -> int:
    """Get the color pair for a given index."""
    return _BACKEND.get_color_pair(i)


# --------------------------------------------------------------------------
