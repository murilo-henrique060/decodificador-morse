import pyqtgraph as pg

pg.setConfigOptions(antialias=False)

class PlotWidget(pg.PlotWidget):
    def __init__(self, color='#00d2ff', y_range=(-10000, 10000)):
        super().__init__()
        self.setBackground('#0a0a0a')
        self.getViewBox().setDefaultPadding(0)
        self.getViewBox().setContentsMargins(0, 0, 0, 0)
        self.getViewBox().setBorder(pg.mkPen(color='#222', width=1))
        self.setMouseEnabled(x=False, y=False)
        self.hideButtons()
        self.setMenuEnabled(False)
        self.showAxis('left', False)
        self.showAxis('bottom', False)
        self.setYRange(*y_range)

        self._curve = self.plot(pen=pg.mkPen(color, width=1.5))

        self._hlines = []

    def addHLine(self, y=0, color='#333'):
        line = self.addLine(y=y, pen=pg.mkPen(color=color, width=1))
        line.setZValue(-10) 
        self._hlines.append(line)

    def clearHLines(self):
        for line in self._hlines:
            self.removeItem(line)
        self._hlines = []

    def setData(self, data):
        self._curve.setData(data)
