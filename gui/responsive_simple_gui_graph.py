# responsive_simple_gui_graph.py
import datetime
import nidaqmx
import pyqtgraph
import sys
import time

from PyQt5.QtCore import (
    Qt, 
    QObject, 
    QThread, 
    pyqtSignal, 
    QSize,
)
from PyQt5.QtWidgets import (
    QApplication, 
    QWidget, 
    QLabel, 
    QPushButton, 
    QLineEdit,
    QFormLayout, 
    QHBoxLayout, 
    QVBoxLayout, 
    QMessageBox, 
    QBoxLayout,
)

from PyQt5.QtGui import QPen, QColor

# Step 1: Creat a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, float)

    def __init__(self, daq):
        super().__init__()
        self.daq = daq
        self.is_running = False
        self.time = 0

    def run(self):
        """Reading task."""
        if not self.is_running:
            self.is_running = True

        while self.is_running == True:   
                measurement = self.daq.read()
                self.progress.emit(self.time, measurement)
                self.time += 1
                time.sleep(1)
        self.finished.emit()
    
    def stop(self):
        self.is_running = False
        self.time = 0
        print('worker finished')

class DAQApp(QWidget):

    def __init__(self):
        super().__init__()
        self.is_reading = False
        self.initializeUI()

    def initializeUI(self):
        """
        Intialize the windows and display its content to the screen.
        """
        self.setGeometry(100, 100, 700, 500)
        self.setWindowTitle('DAQ Application')
        self.formWidgets()

        # To store data from sensor
        self.x = []
        self.y = []

    def formWidgets(self):
        """
        Create widgets that will be used in the application form.
        """
        # Widgets
        device_label = QLabel('Device:')

        self.device_name = QLineEdit()
        self.device_name.setText('cDAQ1Mod1/ai0')
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connectDAQ)

        self.daq_status_label = QLabel()
        self.daq_status_label.setText('DAQ not initialized')

        self.read_button = QPushButton('Read')
        self.read_button.setEnabled(False)
        self.read_button.clicked.connect(self.runReadingTask)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopReadingTask)

        self.save_button = QPushButton('Save')
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.saveDataToFile)

        self.data_label = QLabel()

        # Graph widget
        self.graph_widget = pyqtgraph.PlotWidget()

        self.graph_widget.setBackground('w')
        self.graph_widget.setTitle('Channel 0', color='k')
        self.graph_widget.setLabel('bottom', 'time [s]', color='k')
        self.graph_widget.setLabel('left', 'temperature [deg]', color='k')
        self.graph_widget.showGrid(x=True, y=True)
        self.graph_widget.setXRange(0, 100)
        self.graph_widget.setYRange(0, 100)
        self.line_style = pyqtgraph.mkPen(color='b', w=4.5)

        # Create form layout
        app_form_layout = QFormLayout()

        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_name)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.read_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.save_button)

        app_form_layout.addRow(device_layout)
        app_form_layout.addRow(self.connect_button)
        app_form_layout.addRow('Status:', self.daq_status_label)
        app_form_layout.addRow(buttons_layout)
        app_form_layout.addRow(self.data_label)
        app_form_layout.addRow(self.graph_widget)
        
        self.setLayout(app_form_layout)

    def connectDAQ(self):
        # Creata Task for DAQ (connexion)
        device= self.device_name.text()
        print(device)
        try:
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_thrmcpl_chan(
                device, 
                units=nidaqmx.constants.TemperatureUnits.DEG_C,
                thermocouple_type=nidaqmx.constants.ThermocoupleType.K
            )
            self.task.timing.cfg_samp_clk_timing(2) # Sample time in hz
        except:
            #raise Exception("Cannot create task for accesing DAQ. Check DAQ connection.")
            self.daq_status_label.setText('Connot connect to DAQ!')
        else:
            print('Connected to DAQ.')
            self.daq_status_label.setText('Connected to DAQ')
            self.connect_button.setEnabled(False)
            self.read_button.setEnabled(True)

    def closeEvent(self, event):
        close_question = QMessageBox.question(
            self, 
            'Close program', 
            'Do you want to close the application?', 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if close_question == QMessageBox.Yes:
            # If user closes app without connect to daq
            try:
                self.task.close()
            except AttributeError:
                pass

            # If user closes app without start the reading
            try:
                self.worker.stop()
            except AttributeError:
                pass

            # Accept event and close
            print('Program finished')
            event.accept()
        else:
            event.ignore()

    def reportProgress(self, time, measurement):
        # User to update measure value
        msg = f'x: {time} y: {str(measurement)}'
        #self.data_label.setText(msg)
        print(msg)
        self.addData(time, measurement)
        
    def runReadingTask(self):
        # Clear graph
        self.graph_widget.clear()
        self.x = []
        self.y = []

        # Step 2: Create a QThreaded object
        self.thread = QThread()

        # Step 3: Create a worker object
        self.worker = Worker(self.task)
        
        # Step 4: Move worke to the thread
        self.worker.moveToThread(self.thread)
        
        # Step 5 Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        
        # Step 6: Start threadresponsive_simple_gui_read_continuous_and_exit copy
        self.thread.start()
        
        # Step 7: Final resets
        self.read_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)
        self.thread.finished.connect(lambda: self.read_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.stop_button.setEnabled(False))
        self.thread.finished.connect(lambda: self.save_button.setEnabled(True))

    def stopReadingTask(self):
        self.worker.stop()

    def addData(self, x, y):
        #print('adding data')
        self.x.append(x)
        self.y.append(y)
        
        self.graph_widget.plot(self.x, self.y, pen=self.line_style, symbol='+')

    def saveDataToFile(self):
        print('saving data to file ...')
        self.data_label.setText('saving data to file...')
        # Get current time
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%d-%H-%M-%S')
        
        filename = current_time + '-' + 'temp.txt'
        
        with open(filename, 'w') as txt_file:
            txt_file.write('seconds,temp_deg\n')

            for x, y in zip(self.x, self.y):
                text = str(x) + ',' + str(y) + '\n'
                txt_file.write(text)
        
        print('data saved in', filename)
        self.data_label.setText('data saved in ' + filename)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DAQApp()
    window.show()
    sys.exit(app.exec_())
