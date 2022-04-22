import configparser
import time
from functools import partial

from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QPushButton, QLabel, QSpinBox, QFrame, QPlainTextEdit, \
    QVBoxLayout, QMessageBox

from Worker_Threads import Serial_Reader


class Direct_Control_Interface(QWidget):
    def __init__(self, ser=None):
        super().__init__()
        layout = QGridLayout()

        self.left_group = None
        self.serial_input_box = None
        self.serial_output_box = None
        self.ser = ser
        self.config = configparser.ConfigParser()
        self.config.read("config.ini")

        self.create_top_button_group()
        self.create_serial_input()
        self.create_serial_output()
        self.create_positioning_group()

        layout.addWidget(self.positioning_group, 0, 0, 4, 1)
        layout.addWidget(self.left_group, 0, 4, 2, 2)
        layout.addWidget(self.serial_input_box, 2, 4, 2, 2)
        layout.addWidget(self.serial_output_box, 0, 6, 4, 1)

        self.setWindowTitle("Direct Control")
        self.setWindowIcon(QIcon("Gear-icon"))
        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)

    def create_top_button_group(self):
        self.left_group = QGroupBox("Controls")
        layout = QGridLayout()

        # X Control Buttons
        plus_x10 = QPushButton("X +10")
        plus_x10.clicked.connect(partial(self.move_axis_relative, 'x', 10))
        minus_x10 = QPushButton("X -10")
        minus_x10.clicked.connect(partial(self.move_axis_relative, 'x', -10))

        plus_x1 = QPushButton("X +1")
        plus_x1.clicked.connect(partial(self.move_axis_relative, 'x', 1))
        minus_x1 = QPushButton("X -1")
        minus_x1.clicked.connect(partial(self.move_axis_relative, 'x', -1))

        plus_x001 = QPushButton("X +0.01")
        plus_x001.clicked.connect(partial(self.move_axis_relative, 'x', 0.01))
        minus_x001 = QPushButton("X -0.01")
        minus_x001.clicked.connect(partial(self.move_axis_relative, 'x', -0.01))

        # Y Control Buttons
        plus_y10 = QPushButton("Y +10")
        plus_y10.clicked.connect(partial(self.move_axis_relative, 'y', 10))
        minus_y10 = QPushButton("Y -10")
        minus_y10.clicked.connect(partial(self.move_axis_relative, 'y', -10))

        plus_y1 = QPushButton("Y +1")
        plus_y1.clicked.connect(partial(self.move_axis_relative, 'y', 1))
        minus_y1 = QPushButton("Y -1")
        minus_y1.clicked.connect(partial(self.move_axis_relative, 'y', -1))

        plus_y001 = QPushButton("Y +0.01")
        plus_y001.clicked.connect(partial(self.move_axis_relative, 'y', 0.01))
        minus_y001 = QPushButton("Y -0.01")
        minus_y001.clicked.connect(partial(self.move_axis_relative, 'y', -0.01))

        # Z Control Buttons
        plus_z10 = QPushButton("Z +10")
        plus_z10.clicked.connect(partial(self.move_axis_relative, 'z', 10))
        minus_z10 = QPushButton("Z -10")
        minus_z10.clicked.connect(partial(self.move_axis_relative, 'z', -10))

        plus_z1 = QPushButton("Z +1")
        plus_z1.clicked.connect(partial(self.move_axis_relative, 'z', 1))
        minus_z1 = QPushButton("Z -1")
        minus_z1.clicked.connect(partial(self.move_axis_relative, 'z', -1))

        plus_z001 = QPushButton("Z +0.01")
        plus_z001.clicked.connect(partial(self.move_axis_relative, 'z', 0.01))
        minus_z001 = QPushButton("Z -0.01")
        minus_z001.clicked.connect(partial(self.move_axis_relative, 'z', -0.01))

        # User input control
        x_spinner_label = QLabel("X")
        x_spinner = QSpinBox(minimum=0, maximum=1000)

        y_spinner_label = QLabel("Y")
        y_spinner = QSpinBox(minimum=0, maximum=1000)

        z_spinner_label = QLabel("Z")
        z_spinner = QSpinBox(minimum=0, maximum=1000)

        send_button = QPushButton("Send")
        send_button.clicked.connect(partial(self.move_absolute, x_spinner, y_spinner, z_spinner))

        horizontal_separator = QFrame()
        horizontal_separator.setGeometry(60, 110, 751, 20)
        horizontal_separator.setFrameShape(QFrame.HLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)

        vertical_separator1 = QFrame()
        vertical_separator1.setGeometry(60, 110, 751, 20)
        vertical_separator1.setFrameShape(QFrame.VLine)
        vertical_separator1.setFrameShadow(QFrame.Sunken)

        vertical_separator2 = QFrame()
        vertical_separator2.setGeometry(60, 110, 751, 20)
        vertical_separator2.setFrameShape(QFrame.VLine)
        vertical_separator2.setFrameShadow(QFrame.Sunken)

        # Group Buttons
        # Independent axis control buttons
        layout.addWidget(plus_x10, 0, 0, 1, 4)
        layout.addWidget(minus_x10, 0, 4, 1, 4)
        layout.addWidget(plus_x1, 1, 0, 1, 4)
        layout.addWidget(minus_x1, 1, 4, 1, 4)
        layout.addWidget(plus_x001, 2, 0, 1, 4)
        layout.addWidget(minus_x001, 2, 4, 1, 4)

        layout.addWidget(vertical_separator1, 0, 9, 3, 1)

        layout.addWidget(plus_y10, 0, 10, 1, 4)
        layout.addWidget(minus_y10, 0, 14, 1, 4)
        layout.addWidget(plus_y1, 1, 10, 1, 4)
        layout.addWidget(minus_y1, 1, 14, 1, 4)
        layout.addWidget(plus_y001, 2, 10, 1, 4)
        layout.addWidget(minus_y001, 2, 14, 1, 4)

        layout.addWidget(vertical_separator2, 0, 19, 3, 1)

        layout.addWidget(plus_z10, 0, 20, 1, 4)
        layout.addWidget(minus_z10, 0, 24, 1, 4)
        layout.addWidget(plus_z1, 1, 20, 1, 4)
        layout.addWidget(minus_z1, 1, 24, 1, 4)
        layout.addWidget(plus_z001, 2, 20, 1, 4)
        layout.addWidget(minus_z001, 2, 24, 1, 4)

        layout.addWidget(horizontal_separator, 4, 0, 1, 28)

        layout.addWidget(x_spinner_label, 5, 0)
        layout.addWidget(x_spinner, 5, 1, 1, 6)
        layout.addWidget(y_spinner_label, 5, 7)
        layout.addWidget(y_spinner, 5, 8, 1, 6)
        layout.addWidget(z_spinner_label, 5, 14)
        layout.addWidget(z_spinner, 5, 15, 1, 6)
        layout.addWidget(send_button, 5, 21, 1, 7)

        self.left_group.setLayout(layout)

    def create_serial_input(self):
        self.serial_input_box = QGroupBox("Serial Input")

        self.serial_input_field = QPlainTextEdit()
        self.serial_input_field.setStyleSheet('font-size: 15px')

        send_button = QPushButton("Send")
        send_button.clicked.connect(self.write_serial)
        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.serial_input_field.clear)
        help_button = QPushButton("Help")
        help_button.clicked.connect(self.help_button_info)

        layout = QGridLayout()
        layout.addWidget(self.serial_input_field, 0, 0, 3, 8)
        layout.addWidget(help_button, 3, 0, 1, 2)
        layout.addWidget(clear_button, 3, 2, 1, 2)
        layout.addWidget(send_button, 3, 4, 1, 4)

        self.serial_input_box.setLayout(layout)

    def create_serial_output(self):
        self.serial_output_box = QGroupBox("Serial Output")
        self.serial_output_field = QPlainTextEdit()
        self.serial_output_field.setReadOnly(True)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self.serial_output_field.clear)

        layout = QVBoxLayout()
        layout.addWidget(self.serial_output_field)
        layout.addWidget(clear_button)
        self.serial_output_box.setLayout(layout)

        self.thread = QThread()
        self.worker = Serial_Reader(self.ser)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.update_display)
        self.worker.progress.connect(self.serial_output_field.appendPlainText)
        self.worker.update.connect(self.update)
        self.thread.start()

    def create_positioning_group(self):
        self.positioning_group = QGroupBox("Configure Positions")
        layout = QGridLayout()

        set_home_button = QPushButton("Set Home")
        set_home_button.clicked.connect(partial(self.set_pos, 0))
        move_button = QPushButton("Move Home")
        move_button.clicked.connect(partial(self.move_to_preset, 0))
        layout.addWidget(set_home_button, 0, 0, 1, 4)
        layout.addWidget(move_button, 0, 4, 1, 4)

        for i in range(0, 12, 2):
            set_text = ""
            move_text = ""
            pos = None

            if i // 2 == 0:
                set_text = "Set Home"
                move_text = "Move Home"
                pos = "Home"
            elif i // 2 == 1:
                set_text = "Set Safe"
                move_text = "Move Safe"
                pos = "Safe"
            else:
                set_text = f"Set P{i // 2 - 1}"
                move_text = f"Move P{i // 2 - 1}"
                pos = f"P{i // 2 - 1}"

            set_button = QPushButton(set_text)
            set_button.clicked.connect(partial(self.set_pos, pos))
            move_button = QPushButton(move_text)
            move_button.clicked.connect(partial(self.move_to_preset, pos))

            layout.addWidget(set_button, i, 0, 1, 4)
            layout.addWidget(move_button, i, 4, 1, 4)
            if i != 10:
                horizontal_separator = QFrame()
                horizontal_separator.setGeometry(60, 110, 751, 20)
                horizontal_separator.setFrameShape(QFrame.HLine)
                horizontal_separator.setFrameShadow(QFrame.Sunken)
                layout.addWidget(horizontal_separator, i + 1, 0, 1, 8)

        self.positioning_group.setLayout(layout)

    def move_to_preset(self, pos):
        move = self.config['POSITIONS'][pos]
        print(move)
        self.ser.write(f'G90 {move}\n'.encode())

    def set_pos(self, pos):
        self.worker.set_allowed(False)
        time.sleep(1)
        self.ser.write('?\n'.encode())

        position = self.ser.readline().decode('ascii')
        print(position)

        self.worker.set_allowed(True)

        position = position.split(",")

        x_coord = float(position[1].split(":")[1])
        y_coord = float(position[2])
        z_coord = float(position[3])

        gcode = f"X{x_coord} Y{y_coord} Z{z_coord}"

        self.config.set("POSITIONS", pos, gcode)

        with open('config.ini', 'w') as configfile:
            self.config.write(configfile)

    def move_axis_relative(self, axis, dist):
        self.ser.write(f'G91 {axis}{dist}\n'.encode())

    def move_absolute(self, x, y, z):
        self.ser.write(f'G90 X{x.value()} Y{y.value()} Z{z.value()}\n'.encode())

    def help_button_info(self):
        msg = QMessageBox()
        msg.setWindowTitle("Additional Information")
        msg.setText("Commands:")
        msg.setInformativeText("Enter the $ character for the Grbl help command\n")

        msg.exec_()

    def write_serial(self):
        commands = self.serial_input_field.toPlainText().encode()
        self.ser.write(commands)
        self.serial_input_field.clear()