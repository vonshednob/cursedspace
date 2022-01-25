#!/usr/bin/env python3
import random
import curses
from cursedspace import Application, Key, Panel, ProgressBar


class DemoApplication(Application):
    def __init__(self):
        super().__init__()

    def main(self):
        # Lets make a selfupdating application by setting a timeout for key-capture
        self.screen.timeout(400)
        
        self.init_bars()
        while True:
            self.draw()

            key = self.read_key()

            if key == Key.RESIZE:
                self.resize()
            elif key in [Key.ESCAPE, "q", "^C"]:
                break

    def draw(self):
        # Do update including description for first bar and just update the rest
        for bar in self.bars[1:]:
            bar.update((bar.progress + 1) % 100)
        val = (self.bars[0].progress + 1) % 100
        self.bars[0].update(val, f'Bar 0: {val:03d}')

        for bar in self.bars:
            bar.paint()
            # try:
            #     bar.paint()
            # except:
            #     pass
        curses.doupdate()

    def init_bars(self):
        # Some border combinations to try out!
        border_list = [
            Panel.BORDER_ALL,
            Panel.BORDER_TOP,
            Panel.BORDER_BOTTOM,
            Panel.BORDER_LEFT,
            Panel.BORDER_RIGHT,
            Panel.BORDER_TOP + Panel.BORDER_LEFT,
            Panel.BORDER_TOP + Panel.BORDER_RIGHT,
            Panel.BORDER_BOTTOM + Panel.BORDER_LEFT,
            Panel.BORDER_BOTTOM + Panel.BORDER_RIGHT,
            Panel.BORDER_BOTTOM + Panel.BORDER_TOP,
            Panel.BORDER_LEFT + Panel.BORDER_RIGHT,
        ]

        # Initiate the bars
        h, w = self.size()
        y = 1
        self.bars = []
        for i in range(h-2):
            bar = ProgressBar(
                self,
                border = border_list[i] if i < len(border_list) else Panel.BORDER_NONE,
                width = w - 2,
                pos = (y, 1),
                description = f'Bar {i}',
                color = random.randint(1, 8),
            )
            # Place next bar below this one, taking border size into account
            y += bar.height
            self.bars.append(bar)

            # Dont place too many
            if y > h - 5:
                break

        # Give random initial value
        for bar in self.bars:
            bar.update(random.randint(0, 100))

    def resize(self):
        h, w = self.size()
        for bar in self.bars:
            bar.resize(h, w)


# run the application
DemoApplication().run()
