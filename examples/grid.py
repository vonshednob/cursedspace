#!/usr/bin/env python3
import random
import curses
from cursedspace import Application, Key, Panel, colors, Grid


class Mock(Panel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = "I'm a Hello Panel"
        self.color = random.randint(1, 8)

    def paint(self, clear=False):
        super().paint(clear)
        y, x, h, w = self.content_area()
        for i in range(h):
            self.win.addstr(y + i, x, self.text[:w], colors.attr(self.color))
        self.win.noutrefresh()


class DemoApplication(Application):
    def __init__(self):
        super().__init__()
        # Instantiate Grid with a reference to the application
        self.grid = Grid(self, rows=4, cols=4)

        # Add some panels, the grid cell declaration can be slices and integers
        self.grid.add_panel(slice(0, 4), slice(0, 2), key='big_mock', panel_class=Mock)
        self.grid.add_panel(0, 2, key='small_mock', panel_class=Mock)
        self.grid.add_panel(1, 2, panel_class=Mock)
        self.grid.add_panel(2, 2, panel_class=Mock)
        self.grid.add_panel(3, 2, panel_class=Mock)
        self.grid.add_panel(0, 3, panel_class=Mock)
        self.grid.add_panel(1, 3, panel_class=Mock)
        self.grid.add_panel(2, 3, panel_class=Mock)
        self.grid.add_panel(3, 3, panel_class=Mock)

        # We can easily access all panels in the grid
        for panel in self.grid.panels:
            panel.border = Panel.BORDER_ALL

        # But also use the get-item "key" feature but also index in order of adding to the grid
        self.grid['small_mock'].border = Panel.BORDER_TOP
        self.grid[2].border = Panel.BORDER_BOTTOM
        self.grid[3].border = Panel.BORDER_LEFT
        self.grid[4].border = Panel.BORDER_RIGHT

        # Lets showcase some border combinations
        self.grid[5].border = Panel.BORDER_TOP + Panel.BORDER_LEFT
        self.grid[6].border = Panel.BORDER_TOP + Panel.BORDER_RIGHT
        self.grid[7].border = Panel.BORDER_BOTTOM + Panel.BORDER_LEFT
        self.grid[8].border = Panel.BORDER_BOTTOM + Panel.BORDER_RIGHT

    def draw(self):
        self.grid.paint()
        curses.doupdate()

    def main(self):
        self.resize()

        while True:
            self.draw()
            
            key = self.read_key()
            for panel in self.grid.panels:
                panel.color = random.randint(1, 8)

            if key == Key.RESIZE:
                self.resize()
            elif key in [Key.ESCAPE, "q", "^C"]:
                break

    def resize(self):
        height, width = self.size()
        self.grid.resize(height, width)


# run the application
DemoApplication().run()
