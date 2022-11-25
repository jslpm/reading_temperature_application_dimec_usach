import sys
import os
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        hour = [1,2,3,4,5,6,7,8,9,10]
        temperature_1 = [30,32,34,32,33,31,29,32,35,45]
        temperature_2 = [50,35,44,22,38,32,27,38,32,44]

        # Background color
        self.graphWidget.setBackground('w')
        
        # Graph title
        self.graphWidget.setTitle('Temperature', color='b', size='30pt')
        
        # Graph labels
        styles = {'font-size':'20px'}
        self.graphWidget.setLabel('left', 'Temperature (°C)', **styles)
        self.graphWidget.setLabel('bottom', 'Hour (H)', **styles)
        
        # Axis color
        self.graphWidget.getAxis('left').setTextPen('k')
        self.graphWidget.getAxis('bottom').setTextPen('k')
        
        # Add legend
        self.graphWidget.addLegend()

        # Add grid
        self.graphWidget.showGrid(x=True, y=True)

        # Set axis limits
        # self.graphWidget.setXRange(0, 10, padding=.1)
        # self.graphWidget.setYRange(20, 50, padding=0)
        
        # Plot data
        self.plot(hour, temperature_1, 'sensor1', 'r')
        self.plot(hour, temperature_2, 'sensor2', 'b')

    def plot(self, x, y, plotname, color):
        pen = pg.mkPen(color=color, width=2)
        self.graphWidget.plot(x, y, name=plotname, pen=pen, symbol='+', symboloSize=30, symbolBrush=(color))
        

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()