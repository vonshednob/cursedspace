import curses


class Panel:
    """A generic panel with or without border"""
    BORDER_NONE = 0
    BORDER_TOP = 1
    BORDER_BOTTOM = 2
    BORDER_LEFT = 4
    BORDER_RIGHT = 8
    BORDER_ALL = 15
    BORDER_STYLE = '┌┐└┘─│'

    def __init__(self, app, size=None, pos=None, border=None):
        """app is the cursedspace.Application this panel belongs to
           size is a tuple (height, width)
           pos the position on the application's window (y, x)"""
        self.app = app
        self.dim = (0, 0)
        self.pos = (0, 0)
        self.win = None
        self.border = Panel.BORDER_NONE if border is None else border

        if size is not None:
            self.resize(*size)
            if pos is not None:
                self.move(*pos)

    def destroy(self):
        """Should be called explicitely when closing a panel to restore
        the window(s) "behind" this panel."""
        if self.win is not None:
            del self.win
            self.win = None
            # self.app.refresh(True)

    def __delete__(self):
        self.destroy()

    def handle_key(self, key):
        """Panel specific call-back when a key has been entered by the user

        key is of type cursedspace.Key"""
        pass

    def resize(self, h, w):
        """Resize the panel"""
        self.dim = (h, w)
        if self.win is None:
            self.win = curses.newwin(*self.dim, *self.pos)
        else:
            self.win.resize(*self.dim)
        self.win.clear()
        self.win.noutrefresh()

    def refresh(self, force=False):
        """Refresh the panel

        force will touch the panel's content prior to refreshing"""
        if self.win is None:
            return
        if force:
            self.win.touchwin()
        self.win.noutrefresh()

    def content_area(self):
        """The area available for content, i.e. inside the borders

        Returns a tuple (y, x, height, width)
        """
        y = 0
        x = 0
        h, w = self.dim

        if self.border & Panel.BORDER_TOP != 0:
            y += 1
            h -= 1
        if self.border & Panel.BORDER_LEFT != 0:
            x += 1
            w -= 1
        if self.border & Panel.BORDER_RIGHT != 0:
            w -= 1
        if self.border & Panel.BORDER_BOTTOM != 0:
            h -= 1

        return y, x, h, w

    def focus(self):
        """Move the cursor into this panel"""
        y, x, _, _ = self.content_area()
        
        try:
            self.win.move(y, x)
        except curses.error:
            pass
        self.win.noutrefresh()

        return y, x

    def paint(self, clear=False):
        """Draws the panel into the curses buffer

        Will draw a border based on what self.border is set to.
        If clear is True, it will erase any content of the window first."""
        top_left = 0
        bottom_left = 0
        top_width = self.dim[1]
        bottom_width = self.dim[1]
        left_height = self.dim[0]
        right_height = self.dim[0]
        left_top = 0
        right_top = 0

        if clear:
            self.win.erase()

        if self.border & (Panel.BORDER_TOP + Panel.BORDER_LEFT) != 0:
            self.win.addstr(0, 0, self.BORDER_STYLE[0])
            left_height -= 1
            left_top += 1
            top_width -= 1
            top_left += 1

        if self.border & (Panel.BORDER_TOP + Panel.BORDER_RIGHT) != 0:
            self.win.addstr(0, self.dim[1]-1, self.BORDER_STYLE[1])
            right_height -= 1
            right_top += 1
            top_width -= 1

        if self.border & (Panel.BORDER_BOTTOM + Panel.BORDER_LEFT) != 0:
            self.win.addstr(self.dim[0]-1, 0, self.BORDER_STYLE[2])
            left_height -= 1
            bottom_width -= 1
            bottom_left += 1
            
        if self.border & (Panel.BORDER_BOTTOM + Panel.BORDER_RIGHT) != 0:
            # curses raises an exception when drawing in the lowest, most right
            # cell of the window
            try:
                self.win.addnstr(self.dim[0]-1, self.dim[1]-1, self.BORDER_STYLE[3], 1)
            except curses.error:
                pass
            right_height -= 1
            bottom_width -= 1

        if self.border & Panel.BORDER_TOP != 0:
            self.win.addstr(0, top_left, self.BORDER_STYLE[4]*top_width)

        if self.border & Panel.BORDER_BOTTOM != 0:
            self.win.addstr(self.dim[0]-1, bottom_left, self.BORDER_STYLE[4]*bottom_width)

        if self.border & Panel.BORDER_LEFT != 0:
            for y in range(left_height):
                self.win.addstr(left_top+y, 0, self.BORDER_STYLE[5])

        if self.border & Panel.BORDER_RIGHT != 0:
            for y in range(right_height):
                self.win.addstr(right_top+y, self.dim[1]-1, self.BORDER_STYLE[5])

        self.win.noutrefresh()

    def move(self, y, x):
        """Move the panel"""
        if self.win is None:
            return
        self.pos = (y, x)
        self.win.mvwin(y, x)
        self.app.screen.touchwin()
        self.app.screen.noutrefresh()

