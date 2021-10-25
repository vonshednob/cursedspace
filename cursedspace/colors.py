import collections
import curses
import logging


ColorPair = collections.namedtuple("ColorPair", ['foreground', 'background'], defaults=[-1])


# predefined color identifiers
DEFAULT = ColorPair(-1)
RED = ColorPair(curses.COLOR_RED)
GREEN = ColorPair(curses.COLOR_GREEN)
YELLOW = ColorPair(curses.COLOR_YELLOW)
BLUE = ColorPair(curses.COLOR_BLUE)
MAGENTA = ColorPair(curses.COLOR_MAGENTA)
CYAN = ColorPair(curses.COLOR_CYAN)
BLACK = ColorPair(curses.COLOR_BLACK)
WHITE = ColorPair(curses.COLOR_WHITE)


# internal color numbers, ColorPair -> (internal_color_number, curses.color_pair(internal_color_number))
_color_pairs = {}


def as_colorpair(value):
    """Try to turn value into a ColorPair"""
    if isinstance(value, ColorPair):
        return value

    if isinstance(value, int):
        return ColorPair(value)
    elif isinstance(value, tuple) and len(value) == 2 and all([isinstance(v, int) for v in value]):
        return ColorPair(*value)
    elif isinstance(value, tuple) and all([v is None for v in value]):
        return ColorPair(-1, -1)
    
    raise TypeError(f"Expected int or (int, int), but got {type(value)}")


def register(colorpair):
    """Register a color pair to be used in curses later

    Returns True upon success, False upon failure (logs to 'warning')"""
    global _color_pairs
    colorpair = as_colorpair(colorpair)
    next_id = max([0] + [v[0] for v in _color_pairs.values()]) + 1
    try:
        curses.init_pair(next_id, *colorpair)
        _color_pairs[colorpair] = (next_id, curses.color_pair(next_id))
    except Exception as exc:
        logging.warning(f"Failed to register color {colorpair}: {exc}")
        return False
    return True


def attr(color):
    """Return a curses-like attribute value for 'color'

    'color' may be one of the Colors constants or a tuple
    (foreground, background) of Colors constants.
    """
    global _color_pairs
    color = as_colorpair(color)

    if color == (-1, -1):
        return 0

    if color not in _color_pairs:
        if not register(color):
            # fallback to default colors
            return curses.color_pair(0)
    return _color_pairs[color][1]


def init_colors():
    """Initializes the basic foreground colors and sets up color pairs for each"""
    curses.use_default_colors()
    register(DEFAULT)
    register(BLACK)
    register(WHITE)
    register(RED)
    register(GREEN)
    register(YELLOW)
    register(BLUE)
    register(MAGENTA)
    register(CYAN)

