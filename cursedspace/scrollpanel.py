import curses

from .panel import Panel
from .key import Key


class ScrollPanel(Panel):
    """A generic panel that allows for scrolling content (e.g. a list)

    The content to scroll is per line in self.items.

    After updating the content of self.items you may want to reset
    self.offset and self.cursor to point to a valid element in the list of items.
    Or just set self.cursor and self.scroll to determine the self.offset
    automatically.

    ScrollPanel.SCROLL_MARGIN defines when the list should start scrolling.
    ScrollPanel.SCROLL_PAGING defines whether or not the scrolling should be paging
      instead of line by line.
    ScrollPanel.SCROLL_NEXT and ScrollPanel.SCROLL_PREVIOUS are lists of valid Keys
      that cause the selection of the next/previous item respectively. These can
      trigger scrolling.

    To control how an item is displayed, override the do_paint_item function.
    """
    SCROLL_MARGIN = 5
    SCROLL_PAGING = False
    SCROLL_NEXT = [Key.DOWN]
    SCROLL_PREVIOUS = [Key.UP]
    SCROLL_NEXT_PAGE = [Key.PGDN]
    SCROLL_PREVIOUS_PAGE = [Key.PGUP]
    SCROLL_TO_START = [Key.HOME]
    SCROLL_TO_END = [Key.END]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items = []
        self.cursor = 0
        self.offset = 0
        self.list_height = 1

    @property
    def selected_item(self):
        """The currently selected item"""
        if 0 <= self.cursor < len(self.items):
            return self.items[self.cursor]
        return None

    def do_paint_item(self, y, x, maxwidth, is_selected, item):
        """Here is where you define how to paint that item on the window

        y, x: position where to draw the item
        maxwidth: available space on that line
        is_selected: whether or not that item is the currently selected one
        item: the item to paint
        """
        self.win.addstr(y, x, str(item)[:maxwidth])

    def paint(self, clear=False):
        super().paint(clear)

        for itemidx in range(self.offset, min(self.offset + self.list_height, len(self.items))):
            self.paint_item(itemidx)
        self.win.noutrefresh()

    def jump_to(self, item):
        """Select this item by instance or by index

        Puts the cursor on this item and returns True (you have to call
        paint yourself; most likely with clear=True).
        Returns False if the item is not in the list or the index was out
        of range.
        """
        if isinstance(item, int):
            if item < 0 or item >= len(self.items):
                return False
        else:
            if item not in self.items:
                return False
            item = self.items.index(item)

        self.cursor = item
        self.scroll()
        return True

    def focus(self):
        y, x = 0, 0
        if self.border & Panel.BORDER_TOP != 0:
            y += 1
        if self.border & Panel.BORDER_LEFT != 0:
            x += 1
        y += max(0, min(self.list_height-1, self.cursor - self.offset))

        try:
            self.win.move(y, x)
        except curses.error:
            pass
        self.win.noutrefresh()
        return y, x

    def resize(self, *args):
        super().resize(*args)
        self.calc_list_height()

    def calc_list_height(self):
        self.list_height = self.dim[0]
        if self.border & Panel.BORDER_TOP != 0:
            self.list_height -= 1
        if self.border & Panel.BORDER_BOTTOM != 0:
            self.list_height -= 1

    def paint_item(self, itemidx):
        if not isinstance(itemidx, int):
            itemidx = self.items.index(itemidx)
        y = itemidx - self.offset

        if y < 0 or y >= self.list_height:
            return

        x = 0
        w = self.dim[1] - 1
        if self.border & Panel.BORDER_TOP != 0:
            y += 1
        if self.border & Panel.BORDER_LEFT != 0:
            x += 1
            w -= 1
        if self.border & Panel.BORDER_RIGHT != 0:
            w -= 1

        self.do_paint_item(y, x, w, itemidx == self.cursor, self.items[itemidx])

    def scroll(self):
        self.cursor = max(0, min(self.cursor, len(self.items)-1))

        if self.SCROLL_PAGING:
            if self.cursor - self.offset >= self.list_height - self.SCROLL_MARGIN and self.list_height < len(self.items):
                self.offset = max(0, self.cursor - self.SCROLL_MARGIN)
            elif self.cursor - self.offset < self.SCROLL_MARGIN and self.offset > 0:
                self.offset = max(0, self.cursor - self.list_height + self.SCROLL_MARGIN + 1)
            else:
                return False
        else:
            if self.cursor - self.offset < self.SCROLL_MARGIN:
                self.offset = max(0, self.cursor - self.SCROLL_MARGIN)
            elif self.cursor - self.offset >= self.list_height - self.SCROLL_MARGIN:
                self.offset = min(max(0, self.cursor + self.SCROLL_MARGIN + 1 - self.list_height),
                                  max(0, len(self.items)-self.list_height))
            else:
                return False

        return True

    def handle_key(self, key):
        handled, must_repaint, must_clear = self.handle_scrolling_keys(key)

        if handled and must_repaint:
            self.paint(must_clear)

    def handle_scrolling_keys(self, key):
        """Can be called to handle scrolling keys

        If a scrolling key is found, it will likely update self.cursor.

        May call self.scroll (which updates self.offset).
        May call self.paint_item (and self.do_paint_item subsequently).

        Returns a tuple (handled, must_repaint, must_clear) meaning this:
            * handled: the key was a scrolling key
            * must_repaint: you should call self.paint
            * must_clear: you should pass clear=True to self.paint
        """
        must_repaint = False
        must_clear = False
        cursor = self.cursor
        handled = False

        if key in self.SCROLL_PREVIOUS and cursor > 0:
            cursor -= 1
            handled = True

        elif key in self.SCROLL_NEXT and cursor < len(self.items)-1:
            cursor += 1
            handled = True

        elif key in self.SCROLL_PREVIOUS_PAGE and cursor > 0:
            cursor = max(0, cursor - self.list_height)
            handled = True

        elif key in self.SCROLL_NEXT_PAGE and cursor < len(self.items)-1:
            cursor = min(len(self.items)-1, cursor + self.list_height)
            handled = True

        elif key in self.SCROLL_TO_END:
            cursor = len(self.items)-1
            handled = True

        elif key in self.SCROLL_TO_START:
            cursor = 0
            handled = True

        if self.cursor != cursor and handled:
            old_cursor = self.cursor
            self.cursor = cursor
            must_repaint = self.scroll()
            must_clear = True
            if not must_repaint:
                self.paint_item(old_cursor)
                self.paint_item(self.cursor)

        return handled, must_repaint, must_clear

