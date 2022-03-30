from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox


class SortingMessageBox(QMessageBox):
    def __init__(self, timeout=3, parent=None):
        super(SortingMessageBox, self).__init__(parent)

        self.setWindowTitle("Starting Sort")
        self.setIcon(QMessageBox.Information)
        self.setStandardButtons(QMessageBox.NoButton)
        self.time_to_wait = timeout
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.change_time)
        self.change_time()
        self.timer.start()

    def change_time(self):
        self.setText(f"Sorting will begin in {self.time_to_wait} seconds")
        if self.time_to_wait <= 0:
            self.close()
        self.time_to_wait -= 1

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()