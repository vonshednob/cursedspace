#!/usr/bin/env python3
import curses

from cursedspace import Application, Key, InputLine
from cursedspace import SingleWordCompletionWrapper, Completion


class DemoApplication(Application):
    def __init__(self):
        super().__init__()
        self.input = None

    def main(self):
        words = [Completion.Suggestion("Spanish Inquisition", "nobody"),
                 "parrot",
                 "albatross"]
        self.input = InputLine(self,
                               min(self.size()[1], 30),
                               (3, 3),
                               text="Press Escape or ^C to exit",
                               background='_',
                               completion=SingleWordCompletionWrapper(words))
        self.input.paint()
        self.input.focus()

        while True:
            curses.doupdate()

            key = self.read_key()

            if key in [Key.ESCAPE, "^C"]:
                break
            self.input.handle_key(key)

    def refresh(self, force=False):
        super().refresh(force)
        if self.input is not None:
            self.input.paint()


DemoApplication().run()
