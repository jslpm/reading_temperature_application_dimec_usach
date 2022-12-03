import nidaqmx
import sys

from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit,
    QFormLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class DAQApp(QWidget):

    def __init__(self):
        super().__init__()
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
        device_name = QLineEdit()
        device_name.setText('cDAQ1Mod1/ai0')
        
        self.connect_button = QPushButton('Connect')
        self.connect_button.clicked.connect(self.connectDAQ)

        self.daq_status_label = QLabel()
        self.daq_status_label.setText('DAQ not initialized')

        self.read_button = QPushButton('Read value')
        self.read_button.setEnabled(False)
        self.read_button.clicked.connect(self.read_value)

        self.data_label = QLabel()
        
        # Create form layout
        app_form_layout = QFormLayout()
        app_form_layout.addRow('Device', device_name)
        app_form_layout.addRow(self.connect_button)
        app_form_layout.addRow('Status:', self.daq_status_label)
        app_form_layout.addRow(self.read_button, self.data_label)

        self.setLayout(app_form_layout)

    def connectDAQ(self):
        try:
            self.task = nidaqmx.Task()
            self.task.ai_channels.add_ai_thrmcpl_chan(
                'cDAQ1Mod1/ai0', 
                units=nidaqmx.constants.TemperatureUnits.DEG_C,
                thermocouple_type=nidaqmx.constants.ThermocoupleType.K
            )
            self.task.timing.cfg_samp_clk_timing(1)
        except:
            #raise Exception("Cannot create task for accesing DAQ. Check DAQ connection.")
            self.daq_status_label.setText('Connot connect to DAQ!')
        else:
            print('Connected to DAQ.')
            self.daq_status_label.setText('Connected to DAQ')
            self.connect_button.setEnabled(False)
            self.read_button.setEnabled(True)

    def read_value(self):
        for i in range(5):
            measurement = self.task.read()
            self.data_label.setText(f'count {i+1}: {str(measurement)}')

    def closeEvent(self, event):
        close_question = QMessageBox.question(
            self, 
            'Close program', 
            'Do you want to close the application?', 
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if close_question == QMessageBox.Yes:
            # If user closes app wituoud connect to daq
            try:
                self.task.close()
            except AttributeError:
                pass
            event.accept()
        else:
            event.ignore()
        


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DAQApp()
    sys.exit(app.exec_())
