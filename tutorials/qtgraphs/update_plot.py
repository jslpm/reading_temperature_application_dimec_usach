import sys
import os
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import QtCore
from pyqtgraph import PlotWidget, plot
from random import randint

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        self.x = list(range(100))   # 100 time points
        self.y = [randint(0, 100) for _ in range(100)]  # 100 data points

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
        
        # Line style
        pen = pg.mkPen(color=(255,0,0), width=(2))
        
        # Add legend
        self.graphWidget.addLegend()

        # Add grid
        self.graphWidget.showGrid(x=True, y=True)

        # Set axis limits
        # self.graphWidget.setXRange(0, 10, padding=.1)
        # self.graphWidget.setYRange(20, 50, padding=0)
        
        # Plot data
        self.data_line = self.graphWidget.plot(self.x, self.y, pen=pen)

        # Use QtTimer
        self.timer = QtCore.QTimer()
        self.timer.setInterval(50)  # every 50ms
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):
        self.x = self.x[1:] # remove first element
        self.x.append(self.x[-1] + 1)   # Add a new value 1 higher than the last

        self.y = self.y[1:] # remove the first
        self.y.append(randint(0, 100))  # Add a new random value

        self.data_line.setData(self.x, self.y)  # update data

def main():
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()