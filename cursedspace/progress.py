from .panel import Panel
from . import colors


class ProgressBar(Panel):
    """A generic progressbar that can be updated.
    """

    PROGRESS_SYMBOL = "█"
    NO_PROGRESS_SYMBOL = " "

    def __init__(self, *args, width=None, border=Panel.BORDER_NONE, description='', color=None, **kwargs):
        self.border = border
        if width is None:
            size = None
        else:
            size = (self.height, width)
        kwargs['size'] = size
        kwargs['border'] = border
        super().__init__(*args, **kwargs)

        self.color = color
        self.progress = 0
        self.description = description
        self.description_size = len(description)

    @property
    def height(self):
        h = 1
        if self.border & Panel.BORDER_TOP != 0:
            h += 1
        if self.border & Panel.BORDER_BOTTOM != 0:
            h += 1
        if self.border & (Panel.BORDER_LEFT + Panel.BORDER_RIGHT) != 0:
            h = 3
        return h

    @property
    def top(self):
        if self.border & (Panel.BORDER_LEFT + Panel.BORDER_RIGHT + Panel.BORDER_TOP) != 0:
            return 1
        else:
            return 0

    def update(self, progress, description=None):
        if progress < 0 or progress > 100:
            raise ValueError(f'Progress "{progress}" cannot be less then 0 or higher than 100')
        if description is not None:
            self.description = description[:self.description_size]

        self.progress = progress
        self.refresh()

    def resize(self, h, w):
        super().resize(self.height, w)

    def paint(self, clear=False):
        super().paint(clear=clear)
        _, x, h, w = self.content_area()
        bar_w = w - self.description_size - 2
        y = self.top

        painted = round(bar_w*self.progress/100)
        if painted > bar_w:
            painted = bar_w
        not_painted = bar_w - painted

        bar = self.PROGRESS_SYMBOL*painted + self.NO_PROGRESS_SYMBOL*not_painted

        self.win.addstr(y, x, self.description)
        self.win.addstr(y, x + self.description_size, ' ')
        if self.color is None:
            self.win.addstr(y, x + self.description_size + 1, bar)
        else:
            self.win.addstr(y, x + self.description_size + 1, bar, colors.attr(self.color))

        self.win.noutrefresh()
