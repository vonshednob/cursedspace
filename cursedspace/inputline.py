import logging
import curses

from .panel import Panel
from .key import Key


class InputLine(Panel):
    """A panel that allows for user input as a text input field does.

    Example use case::

        # in your Application's run function:
        edit = InputLine(self, self.size()[1], (0, 0))

        while True:
            key = self.read_key()
            if key == Key.RESIZE:
                edit.resize(self.size()[1])
            elif key == Key.RETURN:
                # user accepted input, check edit.text
                break
            elif key == Key.ESCAPE:
                # user cancelled input
                break
            else:
                edit.handle_key(key)
    """
    def __init__(self, app, width, pos, text="", prefix="", background=' '):
        super().__init__(app, (1, width), pos)
        self.text = text
        self.offset = 0
        self.cursor = 0
        self.margin = 2
        self.background = background
        self.prefix = prefix
        self.read_only = False

    def paint(self, clear=False):
        self.border = Panel.BORDER_NONE
        super().paint(clear)
        self.scroll()
        visible_text = self.text[self.offset:]
        visible_text = visible_text[:self.dim[1]-1-len(self.prefix)]
        self.win.addstr(0, 0, self.background*(self.dim[1]-1))
        self.win.addstr(0, 0, self.prefix)
        self.win.addstr(0, len(self.prefix), visible_text)
        self.win.noutrefresh()

    def focus(self):
        y = 0
        x = self.cursor - self.offset + len(self.prefix)
        try:
            self.win.move(y, x)
        except curses.error:
            pass
        self.win.noutrefresh()
        return y, x

    def scroll(self):
        """Recalculate 'offset' based on window size and cursor position"""
        self.cursor = min(self.cursor, len(self.text))

        if self.margin <= self.cursor - self.offset < self.dim[1] - self.margin - len(self.prefix):
            # no need to change
            return False

        self.offset = max(0, min(len(self.text), self.cursor - self.dim[1] + self.margin + len(self.prefix)))
        return True

    def resize(self, width, compat=None):
        """Change the width of the input field"""
        if compat is not None:
            # some people might call this function with the official (height, width) signature
            # but we're ignoring the height: it's always 1!
            width = compat
        super().resize(1, width)

    def handle_key(self, key):
        must_repaint = False

        if key in [Key.RIGHT]:
            self.cursor = min(len(self.text), self.cursor+1)
            must_repaint = self.scroll()

        elif key in [Key.LEFT]:
            self.cursor = max(0, self.cursor-1)
            must_repaint = self.scroll()

        elif key in [Key.END, "^E"]:
            self.cursor = len(self.text)
            must_repaint = self.scroll()

        elif key in [Key.HOME, "^A"]:
            self.cursor = 0
            must_repaint = self.scroll()

        elif key in [Key.BACKSPACE, "^H"] and self.cursor > 0 and not self.read_only:
            self.text = self.text[:self.cursor-1] + self.text[self.cursor:]
            self.cursor -= 1
            must_repaint = True

        elif key in ["^U"] and not self.read_only:
            self.text = self.text[self.cursor:]
            self.cursor = 0
            must_repaint = True

        elif key in [Key.DELETE] and len(self.text[self.cursor:]) > 0 and not self.read_only:
            self.text = self.text[:self.cursor] + self.text[self.cursor+1:]
            must_repaint = True

        elif len(str(key)) == 1 and not self.read_only:
            self.text = self.text[:self.cursor] + str(key) + self.text[self.cursor:]
            self.cursor += 1
            must_repaint = True

        if must_repaint:
            self.paint()
            self.focus()

