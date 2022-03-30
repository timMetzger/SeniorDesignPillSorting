from PyQt5.QtCore import QObject, pyqtSignal


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
    progress = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self, serial_port, pills, gcode):
        super().__init__()
        self._sorting = True
        self.ser = serial_port
        self.pills = pills
        self.gcode = gcode

        self.pill_counts = list(self.pills.values())

    def sort_and_update(self):
        while True:
            if sum(self.pills.values()) == 0:
                break
            while self._sorting:
                pass

    def set_sorting(self, state):
        self._sorting = state