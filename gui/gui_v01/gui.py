# gui.py
# Features added:
# - Update button for showing connected devices
# TODO:
# - Generate multiple instances of workers for multiplot
# - Separate worker objecto into a new file

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
    QMainWindow,
    QLabel, 
    QPushButton, 
    QLineEdit,
    QFormLayout, 
    QHBoxLayout, 
    QVBoxLayout, 
    QMessageBox, 
    QBoxLayout,
    QStatusBar,
    QTabWidget,
    QComboBox
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

class DAQApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.is_reading = False
        self.initializeUI()

    def initializeUI(self):
        """
        Intialize the windows and display its content to the screen.
        """
        #self.setFixedSize(QSize(400,100))
        #self.setGeometry(100, 100, 400, 100)
        self.setWindowTitle('DAQ Application')
        self.mainForm()

        # To store data from sensor
        self.x = []
        self.y = []

    def mainForm(self):
        """
        Create widgets that will be used in the application form.
        """

        # Create status bar
        self.statusBar = QStatusBar()                        # Create status bar
        self.statusBar.showMessage('NI-DAQ not connected')   # Display initial message
        self.setStatusBar(self.statusBar)                    # Add status bar to main windows

        # Create widget to contain widgets
        self.widgetContainer = QWidget()
        self.setCentralWidget(self.widgetContainer)

        # Create tab bar
        self.tab_bar = QTabWidget()

        # Widgets
        device_label = QLabel('NI-DAQ device')
        device_label.setStatusTip('Select device for measurement')

        # self.device_name = QLineEdit()
        # self.device_name.setText('cDAQ1Mod1/ai0')
        # self.device_name.setStatusTip('Enter device name and channels')
        self.device_name_cb = QComboBox()
        self.device_name_cb.currentTextChanged.connect(self.on_device_name_changed)
        self.device_name_cb.setStatusTip('Select device')

        self.update_device_button = QPushButton('Update')
        self.update_device_button.clicked.connect(self.updateDevice)
        self.update_device_button.setStatusTip('Update list of connected devices')

        channels_label = QLabel('Channels')
        from_label = QLabel('from')
        self.channels_from_cb = QComboBox()
        to_label = QLabel('to')
        self.channels_to_cb = QComboBox()
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.setEnabled(False)
        self.connect_button.clicked.connect(self.connectDAQ)
        self.connect_button.setStatusTip('Connect to NI-DAQ')

        self.daq_status_label = QLabel()
        self.daq_status_label.setText('DAQ not initialized')

        self.read_button = QPushButton('Read')
        self.read_button.setEnabled(False)
        self.read_button.clicked.connect(self.runReadingTask)
        self.read_button.setStatusTip('Read channels from NI-DAQ')

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopReadingTask)
        self.stop_button.setStatusTip('Stop reading from NI-DAQ')

        self.save_button = QPushButton('Save')
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.saveDataToFile)
        self.save_button.setStatusTip('Save data to .txt file')

        self.data_label = QLabel()

        # Create form layout
        self.app_form_layout = QVBoxLayout()

        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_name_cb)
        device_layout.addWidget(self.update_device_button)

        channels_layout = QHBoxLayout()
        channels_layout.addWidget(channels_label)
        channels_layout.addWidget(from_label)
        channels_layout.addWidget(self.channels_from_cb)
        channels_layout.addWidget(to_label)
        channels_layout.addWidget(self.channels_to_cb)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.read_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.save_button)

        self.app_form_layout.addLayout(device_layout)
        self.app_form_layout.addLayout(channels_layout)
        self.app_form_layout.addWidget(self.connect_button)
        self.app_form_layout.addLayout(buttons_layout)
        
        # self.setLayout(app_form_layout)
        self.widgetContainer.setLayout(self.app_form_layout)

    def connectDAQ(self):
        """
        Manage DAQ connection.
        """
        # Get device name enter by user (example: cDAQ1Mod1/ai0)
        device_entered = self.device_name_cb.currentText()
        first_channel = self.channels_from_cb.currentText()
        last_channel = self.channels_to_cb.currentText()

        # Create Task            self.graph_widget[0].setStatusTip(f'Data from channel {ch1}') for DAQ (connexion)
        try:
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_thrmcpl_chan(
                device_entered + '/' + 'ai' + first_channel + ':' + last_channel,
                units=nidaqmx.constants.TemperatureUnits.DEG_C,
                thermocouple_type=nidaqmx.constants.ThermocoupleType.K
            )
            self.task.timing.cfg_samp_clk_timing(2) # Sample time in hz
        except:
            # raise Exception("Cannot create task for accesing DAQ. Check DAQ connection.")
            # self.daq_status_label.setText('Connot connect to DAQ!')
            QMessageBox.critical(self, 'Error', 'Cannot connect to NI-DAQ!', QMessageBox.Ok, QMessageBox.Ok)
        else:
            print('Connected to DAQ.')
            self.daq_status_label.setText('Connected to DAQ')
            QMessageBox.information(self, 'NI-DAQ connection', 'NI-DAQ is now connected', QMessageBox.Ok, QMessageBox.Ok)
            self.statusBar.showMessage('NI-DAQ connected')
            self.connect_button.setEnabled(False)
            self.read_button.setEnabled(True)

            # Create graphs
            # self.generateGraphTabs(first_channel, last_channel)

    def createGraphWidget(self, ch):
        """
        Creates a configured graph widget.
        """
        # Graph widget
        graph_widget = pyqtgraph.PlotWidget()
        graph_widget.setBackground('w')
        graph_widget.setTitle(f'Channel {ch}', color='k')
        graph_widget.setLabel('bottom', 'time [s]', color='k')
        graph_widget.setLabel('left', 'temperature [deg]', color='k')
        graph_widget.showGrid(x=True, y=True)
        graph_widget.setXRange(0, 100)
        graph_widget.setYRange(0, 100)
        
        return graph_widget

    def generateGraphTabs(self, ch1, ch2=None):
        """
        reate graph widget separated by tabs.
        """
        # Create list for collect graph widgets
        self.graph_widget = []

        # Check if one o more channels are specified
        if ch2 == None:
            self.graph_widget.append(self.createGraphWidget(ch1))
            self.tab_bar.addTab(self.graph_widget[0], f'ch{ch1}')
        else:
            list_channels = list(range(ch1, ch2+1))
            for ch in list_channels:
                new_graph_widget = self.createGraphWidget(ch)
                self.graph_widget.append(new_graph_widget)
                self.tab_bar.addTab(new_graph_widget, 'ch' + str(ch))

        # Add tab bar main windows
        self.app_form_layout.addWidget(self.tab_bar)

        # Set minimum width and height of the window
        self.setMinimumWidth(400)
        self.setMinimumHeight(400)

    def closeEvent(self, event):
        # close_question = QMessageBox.question(
        #     self, 
        #     'Close program', 
        #     'Do you want to close the application?', 
        #     QMessageBox.Yes | QMessageBox.No, 
        #     QMessageBox.No
        # )

        # if close_question == QMessageBox.Yes:
        #     # If user closes app without connect to daq
        #     try:
        #         self.task.close()
        #     except AttributeError:
        #         pass

        #     # If user closes app without start the reading
        #     try:
        #         self.worker.stop()
        #     except AttributeError:
        #         pass

        #     # Accept event and close
        #     print('Program finished')
        #     event.accept()
        # else:
        #     event.ignore()

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

    def updateDevice(self):
        """
        Update list of devices connected to computer using nidaqmx API.
        """
        # Get all devices stored in  device_name combobox
        all_cb_device_items = [self.device_name_cb.itemText(i) for i in range(self.device_name_cb.count())]
        # Get devices currently connected
        system = nidaqmx.system.System.local()
        # Iterate through devices
        if system.devices:
            for device in system.devices:
                # print(device)
                # Check if device is already store in device_name combobox
                if device.name not in all_cb_device_items:
                    # Populate combobox with new connected devices
                    self.device_name_cb.addItem(device.name)
        else:
            # Clear combobox when devices are not found
            self.device_name_cb.clear()
            self.channels_from_cb.clear()
            self.channels_to_cb.clear()
            # print('Not devices connected.')

    def on_device_name_changed(self, name):
        """
        Run every time device_name combobox is changed.
        """
        # Get number of analog input channels available in device
        if name:
            system = nidaqmx.system.System.local()
            for device in system.devices:
                if device.name == name:
                    chs = device.ai_physical_chans
                    ch_idx = [ch.name[ch.name.index('/')+3:] for ch in chs]
                    if ch_idx:
                        self.channels_from_cb.addItems(ch_idx)
                        self.channels_to_cb.addItems(ch_idx)
                        self.connect_button.setEnabled(True)
                    else:
                        self.channels_from_cb.clear()
                        self.channels_to_cb.clear()
                        self.connect_button.setEnabled(False)
        else:
            print('No device connected.')
            self.connect_button.setEnabled(False)
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DAQApp()
    window.show()
    sys.exit(app.exec_())
