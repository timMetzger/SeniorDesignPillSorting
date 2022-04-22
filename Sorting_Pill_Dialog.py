from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QGridLayout, QPushButton, QGroupBox, QPlainTextEdit, QVBoxLayout, \
    QMessageBox, QProgressBar

from Worker_Threads import Sorting_Worker
from time import time


class Sorting_Pill_Dialog(QWidget):
    def __init__(self, ser_grbl, ser_uno, pills, gcode, inSteps):
        super().__init__()
        print(gcode)
        self.ser_grbl = ser_grbl
        self.ser_uno = ser_uno
        self.pills = pills
        self.gcode = gcode
        self.inSteps = inSteps

        self.thread_response = False

        self.sorting = True

        self.resume_pause = None
        self.abort = None
        self.progress_bar = None
        self.description_field = None

        self.text = QLabel(f"Sorting Pills")

        self.create_buttons()
        self.create_progress_bar()
        self.start_thread()

        layout = QGridLayout()

        layout.addWidget(self.text, 0, 0)
        layout.addWidget(self.resume_pause, 1, 0, 2, 2)
        layout.addWidget(self.abort, 1, 2, 2, 2)
        layout.addWidget(self.progress_bar, 3, 0, 1, 4)

        self.setWindowTitle("Sorting Pills")
        self.setWindowIcon(QIcon("Pills-icon"))
        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)

        self.start_time = time()

    # Create resume/pause and abort buttons
    def create_buttons(self):
        self.resume_pause = QPushButton("Pause")
        self.resume_pause.clicked.connect(self.change_state)

        self.abort = QPushButton("Abort")
        self.abort.clicked.connect(self.abort_sort)

    # Create sorting worker thread
    def start_thread(self):
        self.thread = QThread()
        self.worker = Sorting_Worker(self.ser_grbl, self.ser_uno,self.pills, self.gcode, self.inSteps, self)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.sort_and_update)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.stepper.connect(self.next_step_box)
        self.worker.finished.connect(self.final_dialog)
        self.thread.start()

    def next_step_box(self):
        msg = QMessageBox()
        msg.setWindowTitle("Proceed or Rerun")
        msg.setText("Proceed to next step or rerun previous cycle")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

        proceed = msg.button(QMessageBox.Yes)
        proceed.setText("Proceed")

        rerun = msg.button(QMessageBox.Cancel)
        rerun.setText("Rerun")

        msg.exec_()

        if msg.clickedButton() == proceed:
            self.worker.increment_pos(1)
        else:
            self.worker.decrement_pos(5)
            self.update_progress_bar(self.progress_bar.value() - 5)


        self.thread_response = True

    # Notify of successful sort
    def final_dialog(self):
        self.thread.terminate()
        final_time = time()

        msg = QMessageBox()
        msg.setWindowTitle("Sorting Complete")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"Sorting has been completed\n Time: {round(final_time - self.start_time,3)} seconds")

        msg.exec_()

        self.close()

    # Creates progress bar
    def create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(self.gcode)-1)
        self.progress_bar.setValue(0)

    def update_progress_bar(self,n):
        self.progress_bar.setValue(n)

    # Change running state when button is pressed
    def change_state(self):
        if self.sorting:
            self.setWindowTitle("Sorting Paused")
            self.resume_pause.setText("Resume")
            self.sorting = False
            self.worker.set_sorting(False)
            self.ser_uno.write(b'hold')

        else:
            self.setWindowTitle("Sorting Pills")
            self.resume_pause.setText("Pause")
            self.sorting = True
            self.worker.set_sorting(True)
            self.ser_uno.write(b'resume')

    # Abort sorting process
    def abort_sort(self):
        self.sorting = False
        self.ser_uno.write(b'abort')
        self.close()

    # Close window
    def closeEvent(self, event):
        self.progress_bar.setValue(0)
        event.accept()