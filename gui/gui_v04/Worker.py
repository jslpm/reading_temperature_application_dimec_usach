from PyQt5.QtCore import (
    QObject, 
    pyqtSignal, 
)
import time

# Step 1: Creat a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int, float)

    def __init__(self, task):
        super().__init__()
        self.task = task[2]
        self.is_running = False
        self.time = 0

    def run(self):
        """Reading task."""
        if not self.is_running:
            self.is_running = True

        while self.is_running == True:
                measurement = self.task.read()
                self.progress.emit(self.task[0].text(), self.time, measurement)
                self.time += 1
                time.sleep(1)
        self.finished.emit()
    
    def stop(self):
        self.is_running = False
        self.time = 0
        print(f'Worker finished for {self.task[0].text()}')
