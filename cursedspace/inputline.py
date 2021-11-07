import logging
import curses
import string

from . import colors
from .panel import Panel
from .scrollpanel import ScrollPanel
from .key import Key


class Completion:
    COLOR = colors.DEFAULT

    KEYS_NEXT_ALTERNATIVE = [Key.DOWN, "^N", Key.TAB]
    KEYS_PREVIOUS_ALTERNATIVE = [Key.UP, "^P"]
    KEYS_SELECT_ALTERNATIVE = [Key.RETURN]
    KEYS_CANCEL_SUGGESTIONS = [Key.ESCAPE, "^C"]

    class SuggestionPanel(ScrollPanel):
        def __init__(self, parent):
            super().__init__(parent.app)

        def do_paint_item(self, y, x, maxwidth, is_selected, item):
            attr = curses.A_REVERSE
            if is_selected:
                attr = curses.A_NORMAL
            label = item[:maxwidth]
            label = label + " "*(maxwidth-len(label)+1)
            try:
                self.win.addstr(y, x, label, attr)
            except curses.error:
                pass

    def __init__(self, inputline):
        self.app = inputline.app
        self.inputline = inputline
        self.suggestion_box_type = self.SuggestionPanel
        # the scrollpanel with the suggestions
        self.suggestions = None

    def handle_key(self, key):
        """When InputLine receives a key, it will call this function

        Be sure to return False if you do not consume the key, because
        only then will InputLine handle the key itself.
        """
        if not self.is_visible:
            return False

        handled = self.suggestions.handle_key(key)

        if not handled:
            if key in self.KEYS_CANCEL_SUGGESTIONS:
                self.close()
                handled = True
            elif key in self.KEYS_SELECT_ALTERNATIVE:
                self.alternative_selected(self.suggestions.selected_item)
                self.close()
                handled = True

            if handled:
                self.app.paint()
        
        return handled

    def alternative_selected(self, alternative):
        """Called when the user selected an alternative from the list of options"""
        self.inputline.replace_word(alternative)

    def paint(self, clear=False):
        if self.is_visible:
            self.suggestions.paint(True)

    def update(self, y, x):
        """Called by the InputLine when the user changed the text

        ``y`` and ``x`` are the absolute coordinates of the cursor
        in respect to the app.screen window.

        To access the current text and the cursor position in the
        text, refer to ``self.inputline.text`` and ``self.inputline.cursor``.
        Or get the current word through ``self.inputline.current_word``.

        In this function you must compile the possible suggestion alternatives
        and call ``self.set_alternatives(alternatives, y, x)``.
        Afterwards you will have to call ``self.app.paint``, too.

        Or, if no alternatives can be suggested, make sure to call
        ``self.close``.
        """
        raise NotImplementedError()

    def autosize(self, y, x):
        """Auto resize the suggestion box with the anchor being at y,x"""
        if not self.is_visible:
            return

        screen_h, screen_w = self.app.size()

        space_below = screen_h - (y+1)
        space_above = y-1
        space_right = screen_w - (x+1)
        height = min([10, len(self.suggestions.items), max(space_below, space_above)])
        width = max([len(item) for item in self.suggestions.items])

        py = y
        px = x

        if width >= screen_w:
            width = 2*width//3

        if space_right < width:
            if x >= width:
                px = x-width
            else:
                px = screen_w - width

        if space_below < height and space_above < height:
            if space_below > space_above:
                height = space_below
            else:
                height = space_above

        if space_below >= height:
            py = y+1
        elif space_above >= height:
            py = y - height - 1

        self.suggestions.resize(height, width)
        self.suggestions.move(py, px)

    def set_alternatives(self, items, pos=None):
        if not self.is_visible:
            if pos is None:
                pos = self.inputline.absolute_cursor
            self.suggestions = self.suggestion_box_type(self)
            if isinstance(self.suggestions, ScrollPanel):
                self.suggestions.wrapping = True
                self.suggestions.SCROLL_NEXT = self.KEYS_NEXT_ALTERNATIVE
                self.suggestions.SCROLL_PREVIOUS = self.KEYS_PREVIOUS_ALTERNATIVE
                self.suggestions.SCROLL_TO_END = []
                self.suggestions.SCROLL_TO_START = []
                self.suggestions.SCROLL_NEXT_PAGE = []
                self.suggestions.SCROLL_PREVIOUS_PAGE = []
                self.suggestions.SCROLL_MARGIN = 1
        else:
            if pos is None:
                pos = self.suggestions.pos[:]
        self.suggestions.items = items
        self.autosize(*pos)

    @property
    def is_visible(self):
        return self.suggestions is not None

    def close(self):
        """Close the suggestions panel

        Returns True if the suggestion box was destroyed, False if nothing was done"""
        if self.is_visible:
            self.suggestions.destroy()
            self.suggestions = None
            return True
        return False


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
    def __init__(self, app, width, pos, text="", prefix="", background=' ', completion=None):
        self.completion = completion(self) if completion is not None else None
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

        if self.completion is not None:
            self.completion.paint(clear)

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

        if self.completion is not None:
            self.completion.autosize(*self.absolute_cursor)

    def current_word(self):
        """Return the span of the current word (the word at the cursor)

        Returns a tuple (start, end) or None if not on a word.
        """
        start = self.cursor

        if len(self.text[start-1:start+1].strip()) == 0:
            return None

        else:
            if start == len(self.text):
                start -= 1
            elif self.text[start] in string.whitespace:
                start -= 1
            end = start

            # move backwards in the word to find the start
            while start >= 0:
                if self.text[start] in string.whitespace:
                    break
                start -= 1
            start += 1

            # move forward in the word to find the end
            while end < len(self.text) and self.text[end] not in string.whitespace:
                end += 1

        return (start, end)

    def replace_word(self, word, move_to_end=True):
        """Replace the word at the cursor position with ``word``

        If the cursor is on a space, the word is inserted before the cursor.

        Unless ``move_to_end`` is set to ``False``, the cursor will be moved
        to the end of the word at the end of the replacing.
        """
        span = self.current_word()

        if span is None:
            self.text = self.text[:self.cursor] + word + self.text[self.cursor:]
            if move_to_end:
                self.cursor = self.cursor + len(word)

        else:
            start, end = span
            self.text = self.text[:start] + word + self.text[end:]
            if move_to_end:
                self.cursor = start + len(word)

        self.paint()

    @property
    def absolute_cursor(self):
        """Return the (y,x) tuple of the absolute cursor position on screen"""
        return self.pos[0], self.pos[1] + self.cursor - self.offset

    def update_completion(self):
        """Trigger .update on the completion component, if there is any"""
        if self.completion is not None:
            self.completion.update(*self.absolute_cursor)

    def handle_key(self, key):
        must_repaint = False
        current_text = self.text

        if not self.read_only and self.completion is not None and self.completion.handle_key(key):
            logging.debug(f"Completion should have handled {key}")
            pass

        elif key in [Key.RIGHT]:
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

        if self.completion is not None and self.text != current_text:
            self.update_completion()

        if must_repaint:
            self.paint()
            self.focus()

