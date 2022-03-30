from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QPlainTextEdit, QVBoxLayout, \
    QMessageBox, QProgressBar

from Worker_Threads import Sorting_Worker


class Sorting_Pill_Dialog(QWidget):
    def __init__(self, ser_grbl, ser_uno, pills, gcode):
        super().__init__()
        self.ser_grbl = ser_grbl
        self.ser_uno = ser_uno
        self.pills = pills
        self.gcode = gcode

        self.sorting = True

        self.resume_pause = None
        self.abort = None
        self.progress_bar = None
        self.description_box = None
        self.description_field = None

        self.text = QLabel(f"Sorting Pills")

        self.create_buttons()
        self.create_progress_bar()
        self.create_description()

        layout = QGridLayout()

        layout.addWidget(self.text, 0, 0)
        layout.addWidget(self.resume_pause, 1, 0, 2, 2)
        layout.addWidget(self.abort, 1, 2, 2, 2)
        layout.addWidget(self.description_box, 3, 0, 2, 4)
        layout.addWidget(self.progress_bar, 5, 0, 1, 4)

        self.setWindowTitle("Sorting Pills")
        self.setWindowIcon(QIcon("Pills-icon"))
        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)

    # Create resume/pause and abort buttons
    def create_buttons(self):
        self.resume_pause = QPushButton("Pause")
        self.resume_pause.clicked.connect(self.change_state)

        self.abort = QPushButton("Abort")
        self.abort.clicked.connect(self.abort_sort)

    # Create remaining pills description
    def create_description(self):
        self.description_box = QGroupBox("Pills Remaining")
        self.description_field = QPlainTextEdit()
        self.description_field.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.description_field)

        self.description_box.setLayout(layout)

        self.thread = QThread()
        self.worker = Sorting_Worker(self.ser_grbl, self.pills, self.gcode)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.sort_and_update)
        self.worker.progress.connect(self.update_description)
        self.worker.finished.connect(self.final_dialog)
        self.thread.start()

    # Updates the description field
    def update_description(self, nums):
        i = 0
        output_str = "Medication".ljust(15) + "Remaining".ljust(15) + "\n"
        for key, val in self.pills.items():
            self.pills[key] = nums[i]
            output_str += f"{key}".ljust(15) + f"{val}".ljust(15)

            i += 1

        self.description_field.clear()
        self.description_field.setPlaceholderText(output_str)

    # Notify of successful sort
    def final_dialog(self):
        self.thread.terminate()

        msg = QMessageBox()
        msg.setWindowTitle("Sorting Complete")
        msg.setIcon(QMessageBox.Information)

        msg.exec_()

        self.close()

    # Creates progress bar
    def create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000)
        self.progress_bar.setValue(0)

    # Change running state when button is pressed
    def change_state(self):
        if self.sorting:
            self.setWindowTitle("Sorting Paused")
            self.resume_pause.setText("Resume")
            self.sorting = False
            self.worker.set_sorting(False)

        else:
            self.setWindowTitle("Sorting Pills")
            self.resume_pause.setText("Pause")
            self.sorting = True
            self.worker.set_sorting(True)

    # Abort sorting process
    def abort_sort(self):
        self.sorting = False
        self.close()

    # Close window
    def closeEvent(self, event):
        event.accept()