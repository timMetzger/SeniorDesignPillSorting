from PyQt5.QtCore import pyqtSignal, QObject
from time import sleep


class Serial_Reader(QObject):
    progress = pyqtSignal(str)
    update = pyqtSignal()


    def __init__(self, serial_port):
        super().__init__()
        self.ser = serial_port
        self._allowed = True

    def update_display(self):
        if self.ser is not None:

            while True:
                while self._allowed:
                    text = self.ser.readline().decode('ascii')
                    if text:
                        self.progress.emit(text)
                        self.update.emit()

    def set_allowed(self, b):
        self._allowed = b


class Sorting_Worker(QObject):
    progress = pyqtSignal(int)
    stepper = pyqtSignal()
    finished = pyqtSignal()


    def __init__(self, serial_port, pills, gcode, inSteps, mainapp):
        super().__init__()
        self._sorting = True
        self.ser = serial_port
        self.pills = pills
        self.gcode = gcode
        self.inSteps = inSteps

        self.app = mainapp

        self.i = 0

        self.pill_counts = list(self.pills.values())

    def sort_and_update(self):
        self.i = 0
        while True:
            while self._sorting:
                if self.i == len(self.gcode) - 1:
                    break
                if self.gcode[self.i].startswith("M05"): # decrement counter
                    if self.inSteps:
                        self.stepper.emit()

                        # Await messagebox to be clicked by main thread
                        while not self.app.thread_response:
                            sleep(.1)

                        self.app.thread_response = False

                    else:
                        self.i += 1

                else:
                    self.ser.write(self.gcode[self.i].encode())
                    self.i += 1

                self.progress.emit(self.i)
                sleep(0.25)

            if self.i == len(self.gcode) - 1:
                break

        self.finished.emit()

    def set_sorting(self, state):
        self._sorting = state

    def decrement_pos(self,j):
        self.i -= j

    def increment_pos(self,j):
        self.i += j