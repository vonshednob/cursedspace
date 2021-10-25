import locale
import curses
import sys

from . import colors
from .key import Key


class Application:
    """A generic application with curses

    Use self.screen for drawing operations.
    """
    def __init__(self):
        self.screen = None
        self.is_initialized = False
        self.preferred_encoding = None
        self._cursor_set = False
        self._original_cursor = 1

    def refresh(self, force=False):
        """Refreshes the screen

        If force is set to True, it will touch the screen first
        to enforce a full refresh"""
        if force:
            self.screen.touchwin()
        self.screen.noutrefresh()

    def size(self):
        """Refreshes the size of the screen and returns the (height,width) tuple"""
        curses.update_lines_cols()
        return self.screen.getmaxyx()

    def main(self):
        """Your entry point for the main loop"""
        raise NotImplementedError()

    def read_key(self):
        """Read the next key press from the system

        Returns a cursedspace.Key instance"""
        return Key.read(self.screen)

    def run(self):
        """The main function to call when actually running the application"""
        exception = None

        try:
            self.init_curses()
            self.main()
        except Exception as exc:
            exception = exc

        self.end_curses()

        if exception is not None:
            raise exception

        return 0

    def show_cursor(self, state):
        """Whether or not to show the cursor

        This is a wrapper for curses.curs_set, but will remember the original
        state of the cursor and restore it when the application ends, so you
        don't have to.
        """
        if isinstance(state, bool):
            state = 1 if state else 0

        try:
            previous_state = curses.curs_set(state)
        except curses.error:
            return

        if not self._cursor_set:
            self._original_cursor = previous_state

    def init_curses(self):
        """Will be called prior to using any curses operations in self.run()

        Normally you should not have to call this."""
        if self.is_initialized:
            return

        locale.setlocale(locale.LC_ALL, '')
        self.preferred_encoding = locale.getpreferredencoding()

        self.screen = curses.initscr()
        curses.def_shell_mode()

        if curses.has_colors():
            curses.start_color()
            colors.init_colors()

        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)

        curses.def_prog_mode()

        self.is_initialized = True

    def end_curses(self):
        self.screen.clear()
        self.screen.refresh()

        if self._cursor_set:
            try:
                curses.curs_set(self._original_cursor)
            except curses.error:
                pass

        try:
            curses.endwin()
        except:
            pass

    def set_term_title(self, title):
        """Attempt to set the title of the terminal emulator"""
        # trying our best
        sys.stdout.write(f'\x1b]0;{title}\x07')
        sys.stdout.write(f'\x1b]2;{title}\x07')
        sys.stdout.flush()

    def __delete__(self):
        self.end_curses()

