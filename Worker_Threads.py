from PyQt5.QtCore import pyqtSignal, QObject
from time import sleep,time
import re


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


    def __init__(self, serial_grbl, serial_uno ,pills, gcode, inSteps, mainapp):
        super().__init__()
        self._sorting = True
        self.ser = serial_grbl
        self.ser_uno = serial_uno
        self.pills = pills
        self.gcode = gcode
        self.inSteps = inSteps

        self.app = mainapp

        self.i = 0

        self.pill_counts = list(self.pills.values())


    def sort_and_update(self):
        self.i = 0
        instructions_completed = 0
        pattern = re.compile("^[^YZM]*$")

        current_x = None
        pos = 0
        self.ser.write(self.gcode[self.i].encode())
        self.i += 1

        while True:
            if self._sorting:
                if self.i < len(self.gcode):
                    self.ser.write(self.gcode[self.i].encode())
                    next_x = pattern.match(self.gcode[self.i])

                    if self.gcode[self.i].startswith("M9"):
                        if self.inSteps:
                            self.stepper.emit()

                            # Await messagebox to be clicked by main thread
                            while not self.app.thread_response:
                                sleep(0.1)

                            self.app.thread_response = False

                    elif next_x is not None:
                        if current_x is None:
                            current_x = self.gcode[self.i]
                            self.ser_uno.write(f"P{pos}".encode())
                        else:
                            if current_x != self.gcode[self.i]:
                                current_x = self.gcode[self.i]
                                pos += 1
                                self.ser_uno.write(f"P{pos}".encode())




                    self.i += 1

                while self.ser.readline().decode('ascii').strip() != 'ok':
                    pass

                instructions_completed += 1
                self.progress.emit(instructions_completed)


            if instructions_completed == len(self.gcode):
                break


        self.ser_uno.write("done".encode())
        self.finished.emit()


    def set_sorting(self, state):
        self._sorting = state

    def decrement_pos(self,j):
        self.i -= j

    def increment_pos(self,j):
        self.i += j