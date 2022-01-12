from .panel import Panel
from . import colors


class ProgressBar(Panel):
    """A generic progressbar that can be updated.
    """

    PROGRESS_SYMBOL = "█"
    NO_PROGRESS_SYMBOL = " "

    def __init__(self, *args, width=None, description='', color=None, **kwargs):
        if width is None:
            size = None
        else:
            size = (3, width)
        kwargs['size'] = size

        super().__init__(*args, **kwargs)
        self.color = color
        self.progress = 0
        self.description = description
        self.description_size = len(description)

    def update(self, progress, description=None):
        if progress < 0 or progress > 100:
            raise ValueError(f'Progress "{progress}" cannot be less then 0 or higher than 100')
        if description is not None:
            self.description = description[:self.description_size]

        self.progress = progress
        self.refresh()

    def resize(self, h, w):
        super().resize(3, w)

    def paint(self, clear=False):
        super().paint(clear=clear)
        h, w = self.dim

        painted = round((w - self.description_size)*self.progress/100)
        if painted + self.description_size + 1 > w:
            painted = w - self.description_size - 1
        not_painted = w - self.description_size - painted - 1
        bar = self.PROGRESS_SYMBOL*painted + self.NO_PROGRESS_SYMBOL*not_painted

        self.win.addstr(1, 0, self.description)
        if self.color is None:
            self.win.addstr(1, self.description_size + 1, bar)
        else:
            self.win.addstr(1, self.description_size + 1, bar, colors.attr(self.color))

        self.win.noutrefresh()
