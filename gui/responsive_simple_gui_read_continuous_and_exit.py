# responsive_simple_gui_read_continuous_and_exit.py
import nidaqmx
import sys
import time

from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QSize
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QFormLayout, QHBoxLayout, QVBoxLayout, QMessageBox)

# Step 1: Creat a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, float)

    def __init__(self, daq):
        super().__init__()
        self.daq = daq
        self.is_running = False
        self.count = 1

    def run(self):
        """Reading task."""
        if not self.is_running:
            self.is_running = True

        while self.is_running == True:   
                measurement = self.daq.read()
                self.progress.emit(self.count, measurement)
                self.count += 1
                time.sleep(1)
        self.finished.emit()
    
    def stop(self):
        self.is_running = False
        self.count = 1
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
        self.setGeometry(100, 100, 400, 100)
        self.setWindowTitle('DAQ Application')
        self.formWidgets()
        self.show()

    def formWidgets(self):
        """
        Create widgets that will be used in the application form.
        """

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

        self.data_label = QLabel()
        
        # Create form layout
        app_form_layout = QFormLayout()

        device_layout = QHBoxLayout()
        device_layout.addWidget(device_label)
        device_layout.addWidget(self.device_name)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.read_button)
        buttons_layout.addWidget(self.stop_button)

        app_form_layout.addRow(device_layout)
        app_form_layout.addRow(self.connect_button)
        app_form_layout.addRow('Status:', self.daq_status_label)
        app_form_layout.addRow(buttons_layout)
        app_form_layout.addRow(self.data_label)
        
        self.setLayout(app_form_layout)

    def connectDAQ(self):
        try:
            device = self.device_name.text()
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_thrmcpl_chan(
                device, 
                units=nidaqmx.constants.TemperatureUnits.DEG_C,
                thermocouple_type=nidaqmx.constants.ThermocoupleType.K
            )
            self.task.timing.cfg_samp_clk_timing(2)
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

    def reportProgress(self, count, measurement):
        # User to update measure value
        msg = f'count {count}: {str(measurement)}'
        self.data_label.setText(msg)
        print(msg)
        
    def runReadingTask(self):
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
        
        # Step 6: Start thread
        self.thread.start()
        
        # Step 7: Final resets
        self.read_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.thread.finished.connect(lambda: self.read_button.setEnabled(True))
        self.thread.finished.connect(lambda: self.stop_button.setEnabled(False))

    def stopReadingTask(self):
        self.worker.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DAQApp()
    sys.exit(app.exec_())
