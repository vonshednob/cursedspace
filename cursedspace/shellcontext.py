import curses


class ShellContext:
    """Conveniently allows you to run a subprocess in curses shell mode

    Example usage::

        # in a cursedspace.Application
        with ShellContext(self.screen):
            subprocess.run(...)
        self.paint(True)
    """
    def __init__(self, win, clear=False):
        self.win = win
        self.clear = clear
        self.cursor_state = None

    def __enter__(self, *args, **kwargs):
        if self.clear:
            self.win.clear()
            self.win.refresh()
            curses.doupdate()

        try:
            self.cursor_state = curses.curs_set(1)
        except curses.error:
            pass

        curses.reset_shell_mode()

    def __exit__(self, *args, **kwargs):
        curses.reset_prog_mode()

        self.win.move(0, 0)
        self.win.clear()

        if self.cursor_state is not None:
            curses.curs_set(self.cursor_state)

        self.win.refresh()

