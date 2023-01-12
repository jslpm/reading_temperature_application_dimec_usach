# gui.py
# Features added:
# - Update button for showing connected devices
# - Generate channel options by thermocouple type
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
    QComboBox,
    QGroupBox,
    QCheckBox,
    QScrollArea,
    QGridLayout
)
from PyQt5.QtGui import QPen, QColor, QPalette
from Worker import Worker

class DAQApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.is_reading = False
        self.is_first_execution = True
        self.thermocouple_types = ['J', 'K', 'T']
        self.container_channels = []
        self.container_thc_types = []
        self.task = None
        self.graph_widget = []
        self.xs = []
        self.ys = []
        self.threads = []
        self.workers = []
        self.chn_thc_list = []
        self.initializeUI()

    def initializeUI(self):
        """
        Intialize the windows and display its content to the screen.
        """
        #self.setFixedSize(QSize(400,100))
        #self.setGeometry(100, 100, 400, 100)
        self.setWindowTitle('DAQ Application')
        self.mainForm()

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
        device_label.setFixedWidth(100)
        device_label.setStatusTip('Select device for measurement')

        self.device_name_cb = QComboBox()
        self.device_name_cb.currentTextChanged.connect(self.on_device_name_changed)
        self.device_name_cb.setStatusTip('Select device')

        self.update_device_button = QPushButton('Update')
        self.update_device_button.clicked.connect(self.updateDevice)
        self.update_device_button.setStatusTip('Update list of connected devices')
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.channels_group = QGroupBox()
        self.channels_group.setStatusTip('Select channels and thermocouple types')
        
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
        self.app_form_layout = QHBoxLayout()

        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_name_cb)
        device_layout.addWidget(self.update_device_button)

        self.channels_layout = QGridLayout()
        self.channels_group.setLayout(self.channels_layout)

        self.scroll_area.setWidget(self.channels_group)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.read_button)
        buttons_layout.addWidget(self.stop_button)
        buttons_layout.addWidget(self.save_button)

        self.controls_layout = QVBoxLayout()

        self.controls_layout.addLayout(device_layout)
        self.controls_layout.addWidget(self.scroll_area)
        self.controls_layout.addWidget(self.connect_button)
        self.controls_layout.addLayout(buttons_layout)
        
        self.app_form_layout.addLayout(self.controls_layout)

        # self.setLayout(app_form_layout)
        self.widgetContainer.setLayout(self.app_form_layout)

    def connectDAQ(self):
        """
        Manage DAQ connection.
        """
        # Get device name enter by user (example: cDAQ1Mod1/ai0)
        device_entered = self.device_name_cb.currentText()
        self.task = nidaqmx.Task()

        # Iterate through device channels
        for item in zip(self.container_channels, self.container_thc_types):
            # Check for selected channels
            ch = item[0]
            thc_type = item[1].currentText()
            
            if ch.isChecked():
                ch_fullname = device_entered + '/' + ch.text()
                # Create Task
                try:
                    self.task.ai_channels.add_ai_thrmcpl_chan(
                    ch_fullname,
                    units=nidaqmx.constants.TemperatureUnits.DEG_C,
                    thermocouple_type=self.to_thc_ni_constant(thc_type)
                    )
                except:
                    print('Cannot connect to DAQ.')
                    # raise Exception(f'Cannot generate task for channel {ch_name}.')
                    self.daq_status_label.setText('Connot connect to DAQ!')
                    QMessageBox.critical(self, 'Error', 'Cannot connect to NI-DAQ!', QMessageBox.Ok, QMessageBox.Ok)
                else:
                    # Set sample time in hz
                    self.task.timing.cfg_samp_clk_timing(2)
                    # Create list for channels and thc types
                    self.chn_thc_list.append([ch.text(), thc_type])

        if self.chn_thc_list:
            # Show successful connection messages
            print('Connected to DAQ.')
            # self.daq_status_label.setText('Connected to DAQ')
            QMessageBox.information(self, 'NI-DAQ connection', 'NI-DAQ is now connected', QMessageBox.Ok, QMessageBox.Ok)
            self.statusBar.showMessage('NI-DAQ connected')
            self.connect_button.setEnabled(False)
            self.read_button.setEnabled(True)

            # Create graphs
            self.generateGraphTabs(self.chn_thc_list)

    def createGraphWidget(self, ch, thc):
        """
        Creates a configured graph widget.
        """
        # Graph widget
        graph_widget = pyqtgraph.PlotWidget()
        graph_widget.setBackground('w')
        graph_widget.setTitle(f'Channel {ch}, {thc}-type', color='k')
        graph_widget.setLabel('bottom', 'time [s]', color='k')
        graph_widget.setLabel('left', 'temperature [deg]', color='k')
        graph_widget.showGrid(x=True, y=True)
        graph_widget.setXRange(0, 100)
        graph_widget.setYRange(0, 100)
        
        return graph_widget

    def generateGraphTabs(self, chn_tch_list):
        """
        Create graph widget separated by tabs.
        """
        # Create list for collect graph widgets
        self.graph_widget = dict()

        # Check if one o more channels are specified
        for items in chn_tch_list:
            new_graph_widget = self.createGraphWidget(items[0], items[1])
            graph_data = [new_graph_widget, [], []]
            self.graph_widget[items[0]] = graph_data
            self.tab_bar.addTab(new_graph_widget, items[0])

        # Add tab bar main windows
        self.app_form_layout.addWidget(self.tab_bar)

        # Set minimum width and height of the window
        self.setMinimumWidth(800)
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

    def reportProgress(self, time, measurements):
        # User to update measure value
        msg = f'x: {time} y: {measurements}'
        #self.data_label.setText(msg)
        print(msg)
        # print('adding data')
        self.line_style = pyqtgraph.mkPen(color='b', w=4.5)
        for i, items in enumerate(self.chn_thc_list):
            ch = items[0]

            self.graph_widget[ch][1].append(time)
            self.graph_widget[ch][2].append(measurements[i])

            x = self.graph_widget[ch][1]
            y = self.graph_widget[ch][2]

            self.graph_widget[ch][0].plot(x, y, pen=self.line_style, symbol='+')
        
    def runReadingTask(self):
        # Clear list variables

        # Step 2: Create QThreaded object
        self.thread = QThread()    

        # Step 3: Create a worker object
        self.worker = Worker(self.task)

        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
            
        # Step 5 Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        # thread.finished.connect(lambda: self.read_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.stop_button.setEnabled(False))
        self.thread.finished.connect(lambda: self.save_button.setEnabled(True))

        # Step 6: Start thread
        self.thread.start()
            
        # Step 7: Final resets
        self.read_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.save_button.setEnabled(False)

    def stopReadingTask(self):
        # Quit threads
        self.thread.quit()
        # Stop workers
        self.worker.stop()
        # Delete workers
        self.worker.deleteLater()
        

    def saveDataToFile(self):
        print('saving data to file ...')
        self.data_label.setText('saving data to file...')
        # Get current time
        now = datetime.datetime.now()
        current_time = now.strftime('%Y-%m-%d-%H-%M-%S')
        
        filename = current_time + '-' + 'temp.txt'

        channels_header = ''
        for items in self.chn_thc_list:
            ch = items[0]
            thc = items[1]
            channels_header += ch + '-' + thc + '-' + 'type' + ','
        
        with open(filename, 'w') as txt_file:
            txt_file.write(f'seconds,{channels_header}\n')

            xs = None
            ys = []

            for data in self.graph_widget.values():
                xs = data[1]
                ys.append(data[2])

            text_to_save = ''
            for i in range(len(xs)):
                text_to_save += str(xs[i]) + ','
                for j in range(len(ys)):
                    text_to_save += str(ys[j][i]) + ','
                text_to_save += '\n'

            txt_file.write(text_to_save)
        
        print('data saved in', filename)
        self.statusBar.showMessage('data saved in ' + filename)

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
            # print('Not devices connected.')

    def on_device_name_changed(self, name):
        """
        Run every time when device_name combobox is changed.
        """
        # Check if device name is not empty
        if name:
            # Read device connected to computer
            system = nidaqmx.system.System.local()
            # Iterate through devices
            for device in system.devices:
                # Check that device name exist
                if device.name == name:
                    # Read analog inputs availables in device
                    chs = device.ai_physical_chans
                    self.generateChannelWidgets(chs)
        else:
            # print('No device connected.')
            self.connect_button.setEnabled(False)

    def generateChannelWidgets(self, channels):
        """
        Creates checkbuttons into Channels group depending on
        the device connected.
        """
        # Get a list of available channels from connected device
        ch_idx = [channel.name[channel.name.index('/')+1:] for channel in channels]
        # print(ch_idx)

        # Check if device has available channels
        if ch_idx:
            # print('Generate channel widgets')
            
            for idx in ch_idx:
                # Create row position
                row = int(idx[2:])
                # Create checkbox channel widget
                channel_ckb = QCheckBox(idx)
                channel_ckb.setMaximumWidth(50)
                # Create thermocouple type combobox
                thc_types_cb = QComboBox()
                thc_types_cb.addItems(self.thermocouple_types)
                thc_types_cb.setMaximumWidth(50)
                # Append widget to list for getting states
                self.container_channels.append(channel_ckb)
                self.container_thc_types.append(thc_types_cb)
                # Add widget to grid layout
                self.channels_layout.addWidget(channel_ckb, row, 0)
                self.channels_layout.addWidget(thc_types_cb, row, 1)
            
            self.connect_button.setEnabled(True)
            self.is_first_execution = False

        elif not ch_idx and self.is_first_execution == False:
            # print('Clear channel widgets')
            # Get number of rows and columns from grid layout
            rows = self.channels_layout.rowCount()
            cols = self.channels_layout.columnCount()
            # Iterate through grid layout to get widget and remove them
            #https://stackoverflow.com/questions/13184250/is-there-any-way-to-remove-a-qwidget-in-a-qgridlayout
            for r in range(rows):
                for c in range(cols):
                    widget_to_remove = self.channels_layout.itemAtPosition(r, c).widget()
                    self.channels_layout.removeWidget(widget_to_remove)
                    # print(r, c, widget_to_remove)
            
            # Delete all reference to channels checkbox
            for item in self.container_channels:
                item.deleteLater()

            # Delete all reference to thermocouple types combobox
            for item in self.container_thc_types:
                item.deleteLater()

            # Clear container lists
            self.container_channels = []
            self.container_thc_types = []

            # Clear tab bar with graphs
            num_tabs = self.tab_bar.count()
            for i in reversed(range(num_tabs)):
                self.tab_bar.removeTab(i)
            
            # Reset channel-thermocouple list
            self.chn_thc_list = []

            # Reset task object
            self.task = None
            
            # Deactivate button for connecting to device
            self.connect_button.setEnabled(False)
            self.read_button.setEnabled(False)

    def to_thc_ni_constant(self, thc_type):
        """
        Convert thermocouple type string (str) to
        ni constant.
        """
        if thc_type == 'J':
            return nidaqmx.constants.ThermocoupleType.J
        elif thc_type == 'K':
            return nidaqmx.constants.ThermocoupleType.K
        elif thc_type == 'T':
            return nidaqmx.constants.ThermocoupleType.T
        else:
            raise Exception('Unknown thermocouple type option.')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DAQApp()
    window.show()
    sys.exit(app.exec_())
