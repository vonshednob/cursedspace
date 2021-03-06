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
        self.wrapping = False

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
        try:
            self.win.addstr(y, x, str(item)[:maxwidth])
        except curses.error:
            pass

    def paint(self, clear=False):
        super().paint(clear)

        y, x, _, w = self.content_area()

        for itemidx in range(self.offset, min(self.offset + self.list_height, len(self.items))):
            self.paint_item(itemidx)
            y += 1

        # Fill the rest with blanks
        for y in range(y, self.list_height+1):
            try:
                self.win.addstr(y, x, " "*w)
            except curses.error:
                pass

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
        y, x, h, _ = self.content_area()
        y = max(y, min(h, y + self.cursor - self.offset))

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
        _, _, self.list_height, _ = self.content_area()

    def paint_item(self, itemidx):
        if not isinstance(itemidx, int):
            itemidx = self.items.index(itemidx)

        y, x, h, w = self.content_area()
        itemy = y + itemidx - self.offset

        if itemy < y or itemy > h:
            return

        self.do_paint_item(itemy, x, w, itemidx == self.cursor, self.items[itemidx])

    def scroll(self):
        items = len(self.items) if self.items is not None else 0
        self.cursor = max(0, min(self.cursor, items-1))
        scroll_margin = min(self.list_height // 2, self.SCROLL_MARGIN)

        if self.SCROLL_PAGING:
            if self.cursor - self.offset >= self.list_height - scroll_margin and \
               self.list_height < items:
                self.offset = max(0, self.cursor - scroll_margin)
            elif self.cursor - self.offset < scroll_margin and self.offset > 0:
                self.offset = max(0, self.cursor - self.list_height + scroll_margin + 1)
            else:
                return False
        else:
            if self.cursor - self.offset < scroll_margin:
                self.offset = max([0,
                                   self.cursor - self.list_height,
                                   self.cursor - scroll_margin])
            if self.cursor - self.offset >= self.list_height - scroll_margin:
                self.offset = max(0,
                                  self.cursor
                                  + min(scroll_margin, len(self.items) - self.cursor)
                                  - self.list_height)
            else:
                return False

        return True

    def handle_key(self, key):
        """Handle user input key

        Returns True if handled, False otherwise
        """
        handled, must_repaint, must_clear = self.handle_scrolling_keys(key)

        if handled and must_repaint:
            self.paint(must_clear)

        return handled

    def select_next(self):
        """Move the cursor to the next item and update the representation

        Returns True if repaint required, otherwise False"""
        if self.wrapping:
            index = (self.cursor+1) % len(self.items)
        else:
            index = min(self.cursor+1, len(self.items)-1)
        return self._select_by_index(index)

    def select_previous(self):
        """Move the cursor to the previous item and update the representation

        Returns True if repaint required, otherwise False"""
        if self.wrapping:
            index = (self.cursor-1) % len(self.items)
        else:
            index = max(self.cursor-1, 0)
        return self._select_by_index(index)

    def _select_by_index(self, index):
        """Move the cursor to item with index

        Return True if repaint is required, False otherwise

        If False is returned the list may or may not have updated
        and repainted the old and the new element.
        """
        must_repaint = False
        if index != self.cursor:
            old_cursor = self.cursor
            self.cursor = index
            must_repaint = self.scroll()
            if not must_repaint:
                self.paint(old_cursor)
                self.paint(self.cursor)
        return must_repaint

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

        if key in self.SCROLL_PREVIOUS:
            if cursor <= 0:
                if self.wrapping:
                    cursor = len(self.items) - 1
            else:
                cursor -= 1
            handled = True

        elif key in self.SCROLL_NEXT:
            if cursor == len(self.items)-1:
                if self.wrapping:
                    cursor = 0
            else:
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

        if handled:
            must_repaint = self._select_by_index(cursor)
            must_clear = True

        return handled, must_repaint, must_clear
