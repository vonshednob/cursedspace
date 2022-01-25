from .panel import Panel


class Grid:
    """A generic grid of panel-type objects that allows for any rectangular tiling.
    """

    def __init__(self, app, rows, cols, size=None, column_sep=0, row_sep=0):
        self.app = app
        self.cols = cols
        self.rows = rows
        self.size = size
        self.panels = []
        self._panel_data = []
        self.keys = []
        self.column_sep = column_sep
        self.row_sep = row_sep

    def fill(self, **kwargs):
        """Fill the Grid with panels"""
        for i in range(self.cols):
            for j in range(self.rows):
                self.add_panel(j, i, **kwargs)

    def cell_size(self):
        height, width = self.size
        return height//self.rows - self.row_sep*self.rows, width//self.cols - self.column_sep*self.cols

    def add_panel(self, rows, cols, key=None, panel_class=Panel, args=None, kwargs=None):
        """Add a panel to the grid.

        cols and rows denote the grid-position of the panel and 
        can either be integer indecies or a slice to span 
        multiple grid-cells.

        Returns the panel object that is being stored in the grid.

        Args and kwargs denote the additional arguments to supply 
        to the panel instansiation.
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        if key is not None and key in self.keys:
            raise ValueError(f'Key "{key}" already exists in Grid')

        pos = [None, None]
        size = [None, None]
        if isinstance(rows, slice):
            rows = list(range(self.rows))[rows]
            size[0] = len(rows)
            pos[0] = rows[0]
        else:
            size[0] = 1
            pos[0] = rows

        if isinstance(cols, slice):
            cols = list(range(self.cols))[cols]
            size[1] = len(cols)
            pos[1] = cols[0]
        else:
            size[1] = 1
            pos[1] = cols

        self._panel_data.append([size, pos])
        panel = panel_class(
            self.app, 
            *args, 
            **kwargs
        )

        self.panels.append(panel)
        self.keys.append(key)

    def remove_panel(self, key):
        """Remove a panel from the grid."""
        if isinstance(key, str):
            ind = self.keys.index(key)
        elif isinstance(key, int):
            ind = key
        elif isinstance(key, Panel):
            ind = self.panels.index(key)
        else:
            raise TypeError(f'Key type {type(key)} not recoginzed for deleting panel from Grid')

        del self.panels[ind]
        del self._panel_data[ind]
        del self.keys[ind]

    def resize(self, height, width):
        """Resize the grid"""
        self.size = (height, width)
        cy, cx = self.cell_size()

        for panel, (size, pos) in zip(self.panels, self._panel_data):
            sy = size[0]*cy + (size[0] - 1)*self.row_sep
            sx = size[1]*cx + (size[1] - 1)*self.column_sep
            py = pos[0]*(cy + self.row_sep) + self.row_sep
            px = pos[1]*(cx + self.column_sep) + self.column_sep

            panel.resize(sy, sx)
            panel.move(py, px)

    def refresh(self, force=False):
        """Refresh the grid"""
        for panel in self.panels:
            panel.refresh(force=force)

    def paint(self, clear=False):
        """Paint the grid"""
        for panel in self.panels:
            panel.paint(clear=clear)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.panels[self.keys.index(key)]
        elif isinstance(key, int):
            return self.panels[key]
        else:
            raise TypeError(f'Key type {type(key)} not recoginzed for Grid indexing')
