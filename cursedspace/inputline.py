"""A single line of user input with optional completion"""
import logging
import curses
import string

from . import colors
from .panel import Panel
from .scrollpanel import ScrollPanel
from .key import Key


class Completion:
    """A completion/suggestion box for InputLine

    This allows you to add autocompletion/suggestions to an InputLine
    component.

    You will have to derive your own variant from this though and implement
    `update`.

    Have a look at the sample `SingleWordCompletion` to see what that could
    look like.
    """
    class Suggestion:
        def __init__(self, text, label=None):
            self.text = text
            self.label = label

        def __str__(self):
            if self.label is not None:
                return self.label
            return self.text

        def __lt__(self, other):
            return str(self) < str(other)

    COLOR = colors.DEFAULT
    ALT_COLOR = colors.DEFAULT

    MAX_HEIGHT = 10
    """Maximum height of the suggestion window"""
    MAX_WIDTH = -1
    """Maximum width of the suggestion window

    -1 means that it tries to fit the longest suggestion."""

    KEYS_NEXT_ALTERNATIVE = [Key.DOWN, "^N", Key.TAB]
    KEYS_PREVIOUS_ALTERNATIVE = [Key.UP, "^P"]
    KEYS_SELECT_ALTERNATIVE = [Key.RETURN]
    KEYS_CANCEL_SUGGESTIONS = [Key.ESCAPE, "^C"]

    class SuggestionPanel(ScrollPanel):
        def __init__(self, parent):
            super().__init__(parent.app)
            self.color = parent.COLOR
            self.alt_color = parent.ALT_COLOR

        def do_paint_item(self, y, x, maxwidth, is_selected, item):
            attr = curses.A_REVERSE + colors.attr(self.alt_color)
            if is_selected:
                attr = curses.A_NORMAL
                attr += colors.attr(self.color)
            if isinstance(item, Completion.Suggestion):
                label = item.label if item.label is not None else item.text
            else:
                label = str(item)
            label = label[:maxwidth]
            label = label + " "*(maxwidth-len(label)+1)
            try:
                self.win.addstr(y, x, label[:maxwidth], attr)
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
                self.app.refresh(True)

        return handled

    def alternative_selected(self, alternative):
        """Called when the user selected an alternative from the list of options"""
        if isinstance(alternative, Completion.Suggestion):
            alternative = alternative.text
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
        if not self.is_visible or \
           self.suggestions is None or \
           self.suggestions.items is None:
            return

        screen_h, screen_w = self.app.size()

        space_below = screen_h - (y+1)
        space_above = y-1
        space_right = screen_w - (x+1)
        height = min([self.MAX_HEIGHT,
                      len(self.suggestions.items),
                      max([space_below, space_above])])
        max_width = self.MAX_WIDTH
        if max_width < 0:
            max_width = screen_w-2
        width = min([screen_w-2,
                     max_width,
                     max([len(item.label)
                          if isinstance(item, Completion.Suggestion) else len(str(item))
                          for item in self.suggestions.items])])

        py = y
        px = x

        # position on the horizontal axis
        if space_right >= width:
            # all fits nicely right of the anchor
            px = x + 1
        else:
            # all fits, but left of the anchor
            px = x + (space_right - width)

        # position vertically
        if space_below >= height:
            # all fits nicely below the input box
            py = y + 1
        else:
            # fits, but only above
            py = y - height

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
        self.suggestions.items = items[:]
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


class SingleWordCompletion(Completion):
    """An example implementation of a completion

    This will provide autocompletion/suggestion for the first word
    that the user types/might type in the input line.

    To use it, pass SingleWordCompletionWrapper(list_of_words) to the input
    line like this:

        words = ["brick", "elbow", "pudding"]
        edit = InputLine(self, self.size()[1], (0, 0),
                         completion=SingleWordCompletionWrapper(words))

    or instead assign the `completion` property afterwards:

        edit = InputLine(self, self.size()[1], (0, 0))
        edit.completion = SingleWordCompletion(edit, words)

    You can also use Completion.Suggestion to select by label and insert
    other text:

        suggestions = [Completion.Suggestion(*pair)
                       for pair in [("Spanish Inquisition", "nobody"),
                                    ("I'm not dead!", "parrot")]]
        edit.completion = SingleWordCompletion(edit, suggestions)
    """
    def __init__(self, inputline, words):
        super().__init__(inputline)
        self.words = words

    def update(self, y, x):
        text = self.inputline.text[:self.inputline.cursor]
        if text.endswith(' '):
            text = ''
        else:
            text = text.split(' ')[-1]

        options = [word
                   for word in sorted(self.words, key=lambda a: str(a))
                   if (isinstance(word, Completion.Suggestion) and word.label.startswith(text))
                      or str(word).startswith(text)]
        if len(options) == 1 and \
           ((isinstance(options[0], Completion.Suggestion) and options[0].label == text)
                   or str(options[0]) == text):
            # only available option typed out
            self.close()
        elif len(options) > 0:
            # there are options? show them
            self.set_alternatives(options, (y, x))
        elif self.is_visible:
            # no options, but the box is still visible? close it
            self.close()


def SingleWordCompletionWrapper(words):
    """Convenience wrapper for SingleWordCompletion"""
    def wrapped(inputline):
        return SingleWordCompletion(inputline, words)
    return wrapped


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

    The input line allows the use of a completion box. To use it, just provide
    an instance of Completion (you will have to derive your own though):

        class MyFancyCompletion(Completion):
            def update(self, y, x):
                self.set_alternatives(["fancy"], (y, x))

        edit = InputLine(self, self.size()[1], (0, 0), completion=MyFancyWordCompletion)

    Or assign the InputLine.completion parameter later to your instance:

        edit = InputLine(self, self.size()[1], (0, 0))
        edit.completion = MyFancyCompletion(edit)
    """
    def __init__(self, app, width, pos, text="", prefix="", background=' ', completion=None):
        self.completion = None
        super().__init__(app, (1, width), pos)
        self.completion = completion(self) if completion is not None else None
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
