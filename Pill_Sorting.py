# By: Timothy Metzger
from PyQt5.QtWidgets import (QApplication, QLabel, QProgressBar, QPushButton, QTableView, QWidget,
                             QHBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLineEdit, QVBoxLayout,
                             QHeaderView, QMenuBar, QActionGroup, QAction, QMessageBox, QSpinBox, QPlainTextEdit,
                             QFrame,QSizePolicy,
                             QDoubleSpinBox)

from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QObject, QTimer ,QThread, pyqtSignal
import serial
import serial.tools.list_ports
from functools import partial
import configparser


class Pill_Sorting_Interface():
    def __init__(self, scripts):
        self.app = QApplication([])
        self.scripts = scripts
        self.ser_grbl = None
        self.ser_uno = None
        self.configurator = None
        self.controller = None
        self.sorter = None
        self.current_selection = None
        self.current_selection_string = None
        self.gcode = None

        self.config = "config.ini"

        self.menu_bar = QMenuBar()
        self.set_com_ports()
        if self.ser_grbl is not None and self.ser_uno is not None:

            self.create_table()
            self.create_top_right_window()
            self.create_bottom_right_window()
            #self.create_progress_bar()
            self.create_menu_bar()

            self.window = QWidget()

            main_layout = QGridLayout()
            main_layout.addWidget(self.menu_bar, 0, 0)
            main_layout.addWidget(self.left_window, 1, 0, 4, 3)
            main_layout.addWidget(self.top_right_window, 1, 3)
            main_layout.addWidget(self.bottom_right_window, 2, 3)
            #main_layout.addWidget(self.progress_bar, 3, 3)
            main_layout.setRowMinimumHeight(0, 25)
            main_layout.setColumnMinimumWidth(1, 750)
            main_layout.setColumnMinimumWidth(3, 250)
            main_layout.setRowMinimumHeight(1, 500)
            main_layout.setColumnStretch(3, 1)
            main_layout.setColumnStretch(0, 2)

            self.window.setWindowTitle("Pill Sorting Interface")
            self.window.setLayout(main_layout)
            self.window.setWindowIcon(QIcon('Pills-icon.png'))
            self.window.show()
        else:
            self.serial_not_set()

        self.app.exec()

    # Create table and table search field
    def create_table(self):
        self.left_window = QGroupBox("Open Prescriptions")

        self.model = QStandardItemModel(len(self.scripts), len(self.scripts[0]) - 3)
        self.model.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Age", "Address"])

        for i, user in enumerate(self.scripts):
            for j, key in enumerate(user.keys()):
                if key != "prescription" and key != "frequency" and key != "days_of_week":
                    self.model.setItem(i, j, QStandardItem(user[key]))

        filter_model = QSortFilterProxyModel()
        filter_model.setSourceModel(self.model)
        filter_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        filter_model.setFilterKeyColumn(2)

        search_bar = QLineEdit()
        search_bar.setStyleSheet('font-size: 15px')
        search_bar.setPlaceholderText("Search by last name")
        layout = QHBoxLayout()
        label = QLabel("Search")
        layout.addWidget(label)
        layout.addWidget(search_bar)
        search_bar.textChanged.connect(filter_model.setFilterRegExp)

        self.table = QTableView()
        self.table.setStyleSheet('font-size: 15px')

        self.table.setModel(filter_model)
        self.table.selectionModel().selectionChanged.connect(self.update_information)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout = QVBoxLayout()
        layout.addWidget(search_bar)
        layout.addWidget(self.table)

        self.left_window.setLayout(layout)

    # Creates prescription information field
    def create_top_right_window(self):
        self.top_right_window = QTextEdit()
        self.top_right_window.setStyleSheet('font-size: 15px')
        self.top_right_window.setPlainText("Prescription Information")
        self.top_right_window.setReadOnly(True)

    # Creates start,pause,abort button field
    def create_bottom_right_window(self):
        self.bottom_right_window = QGroupBox("Controls")

        self.scan_rfid_button = QPushButton("Scan RFID")
        self.scan_rfid_button.clicked.connect(self.scan_rfid)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_sort)

        layout = QGridLayout()
        layout.addWidget(self.scan_rfid_button,0,0,1,3)
        layout.addWidget(self.start_button,1,0,1,3)

        self.bottom_right_window.setLayout(layout)

    # Creates menu bar
    def create_menu_bar(self):
        self.menu_bar = QMenuBar()

        tools = self.menu_bar.addMenu("Tools")
        tools.addAction("Configuration", self.start_configurator)
        tools.addAction("Direct Control", self.start_direct_control)

    # Starts configuration tool
    def start_configurator(self):
        if self.configurator is None:
            self.configurator = Configuration_Interface(self.ser_grbl)
        self.configurator.show()

    # Starts the direct control tool
    def start_direct_control(self):
        if self.controller is None:
            self.controller = Direct_Control_Interface(self.ser_grbl)
        self.controller.show()

    def start_sorter(self):
        if self.sorter is None:
            self.sorter = Sorting_Pill_Dialog(self.ser_grbl,self.ser_uno,self.current_selection['prescription'],self.gcode)
        self.sorter.show()

    # Set the serial communication attribute
    def set_com_ports(self):
        ports = serial.tools.list_ports.comports()
        for i, port in enumerate(ports):
            if port.description.startswith("Arduino"):
                self.ser_uno = serial.Serial(port=port.device,baudrate=115200,timeout=1)
            elif port.description.startswith("USB-SERIAL CH340"):
                self.ser_grbl = serial.Serial(port=port.device,baudrate=115200,timeout=1)

    # Display messagebox that serial ports are not connected
    def serial_not_set(self):
        msg = QMessageBox()
        msg.setWindowTitle("Missing Serial Port")
        msg.setText("Please connect both USBs")
        msg.setInformativeText("If both USBs are connected and you are still getting this error please try different ports")
        msg.setIcon(QMessageBox.Critical)

        msg.exec_()

    # Scan rfid sticker
    def scan_rfid(self):
        self.ser_uno.write(b'scan')
        rfid_info = self.ser_uno.readline()

    # Begin sorting process
    def start_sort(self):
        if self.current_selection is not None:
            self.ser_uno.write(b'start')

            msg = QMessageBox()
            msg.setWindowTitle("Load Medication")
            msg.setText("Please load medication")
            msg.setInformativeText(self.current_selection_string)
            msg.setIcon(QMessageBox.Information)

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            response = msg.exec_()

            if response == QMessageBox.Ok:
                self.generate_gcode()
                starting_msg = SortingMessageBox(timeout=5)
                starting_msg.exec_()
                self.start_sorter()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("No Prescription Selected")
            msg.setText("Please select a prescription from the table or use an RFID tag")
            msg.setIcon(QMessageBox.Critical)

            msg.exec_()

    # Updates the prescriptions information field
    def update_information(self, selected, deselected):
        try:
            item = selected.indexes()[0]
            self.current_selection = self.scripts[item.row()]

            script_info = self.scripts[item.row()]["prescription"]
            script_string = "Slot".ljust(15) + "Medication".ljust(20) + "\n"
            script_string += "-"*30+"\n"
            i = 1
            for key, val in script_info.items():
                script_string += f"Slot {i}".ljust(15) + f"{key}: {val}".ljust(20)+"\n"
                i += 1

            self.current_selection_string = script_string
            self.top_right_window.setPlainText(script_string)
        except IndexError:
            print("IndexError")

    # Generate the gcode commands for sorting
    def generate_gcode(self):
        config = configparser.ConfigParser()
        config.read(self.config)

        home = config['POSITIONS']['home']
        safe = config['POSITIONS']['safe']
        p1 = float(config['POSITIONS']['p1'])
        p2 = float(config['POSITIONS']['p2'])

        gap = p2 - p1

        self.gcode = []

        # Sort a single medication type at a time
        for i, val in enumerate(self.current_selection['prescription'].values()):
            current_slot = p1

            # Get frequency and days of the week
            freq = self.current_selection['frequency'][i]
            days = [j for j, val in enumerate(self.current_selection['days_of_week'][i]) if val]

            for day in days:
                # Rotate sorted pill bin to appropriate day
                self.gcode.append(f'G90 Y{day}\n') # TODO this will need tweaking

                # Drop freq number of pills in the corresponding day
                for _ in range(freq):
                    self.gcode.append(f'G90 X{current_slot}\n')    # move to slot
                    self.gcode.append(f'M03\n')                    # spindle on
                    self.gcode.append('G90 Z-10\n')                # descend
                    self.gcode.append('G90 Z0\n')                  # ascend
                    self.gcode.append(f'G90 {home}\n')             # return to drop
                    self.gcode.append(f'M05\n')                    # spindle off

            current_slot += gap



class Direct_Control_Interface(QWidget):
    def __init__(self, ser=None):
        super().__init__()
        layout = QGridLayout()

        self.left_group = None
        self.serial_input_box = None
        self.serial_output_box = None
        self.ser = ser

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

        plus_x001 = QPushButton("X +0.001")
        plus_x001.clicked.connect(partial(self.move_axis_relative, 'x', 0.001))
        minus_x001 = QPushButton("X -0.001")
        minus_x001.clicked.connect(partial(self.move_axis_relative, 'x', -0.001))

        # Y Control Buttons
        plus_y10 = QPushButton("Y +10")
        plus_y10.clicked.connect(partial(self.move_axis_relative, 'y', 10))
        minus_y10 = QPushButton("Y -10")
        minus_y10.clicked.connect(partial(self.move_axis_relative, 'y', -10))

        plus_y1 = QPushButton("Y +1")
        plus_y1.clicked.connect(partial(self.move_axis_relative, 'y', 1))
        minus_y1 = QPushButton("Y -1")
        minus_y1.clicked.connect(partial(self.move_axis_relative, 'y', -1))

        plus_y001 = QPushButton("Y +0.001")
        plus_y001.clicked.connect(partial(self.move_axis_relative, 'y', 0.001))
        minus_y001 = QPushButton("Y -0.001")
        minus_y001.clicked.connect(partial(self.move_axis_relative, 'y', -0.001))

        # Z Control Buttons
        plus_z10 = QPushButton("Z +10")
        plus_z10.clicked.connect(partial(self.move_axis_relative, 'z', 10))
        minus_z10 = QPushButton("Z -10")
        minus_z10.clicked.connect(partial(self.move_axis_relative, 'z', -10))

        plus_z1 = QPushButton("Z +1")
        plus_z1.clicked.connect(partial(self.move_axis_relative, 'z', 1))
        minus_z1 = QPushButton("Z -1")
        minus_z1.clicked.connect(partial(self.move_axis_relative, 'z', -1))

        plus_z001 = QPushButton("Z +0.001")
        plus_z001.clicked.connect(partial(self.move_axis_relative, 'z', 0.001))
        minus_z001 = QPushButton("Z -0.001")
        minus_z001.clicked.connect(partial(self.move_axis_relative, 'z', -0.001))

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
            set_button = QPushButton(f"Set P{i // 2}")
            set_button.clicked.connect(partial(self.set_pos, i // 2))
            move_button = QPushButton(f"Move P{i // 2}")
            move_button.clicked.connect(partial(self.move_to_preset, i // 2))

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
        pass
        # TODO move to preset pos

    def set_pos(self, pos):
        # TODO set position number to coords given by grbl
        pass

    def move_axis_relative(self, axis, dist):
        self.ser.write(f'G91 {axis}{dist}\n'.encode())

    def move_absolute(self, x,y,z):
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

class Configuration_Interface(QWidget):
    def __init__(self, ser):
        super().__init__()
        self.ser = ser
        layout = QGridLayout()

        self.create_fields()
        layout.addWidget(self.settings_group, 0, 0)

        self.setWindowTitle("Configuration")
        self.setWindowIcon(QIcon("Gear-icon"))
        self.setLayout(layout)
        self.setWindowModality(Qt.ApplicationModal)

    def create_fields(self):
        fields = ["Step Pulse", "Step Idle Delay", "Step Port Invert Mask", "Dir Port Invert Mask",
                  "Step Enable Invert", "Limit Pins Invert",
                  "Probe Pin Invert", "Status Report Mask", "Junction Deviation", "Arc Tolerance", "Report Inches",
                  "Soft Limits", "Hard Limits",
                  "Homing Cycle", "Homing Dir Invert Mask", "Homing Feed", "Homing Seek", "Homing Debounce",
                  "Homing Pull-Off", "X Step/mm", "Y Step/mm", "zZ Step/mm",
                  "X Max Rate", "Y Max Rate", "Z Max Rate", "X Accel", "Y Accel", "Z Accel", "X Max Travel",
                  "Y Max Travel", "Z Max Travel"]

        self.settings_group = QGroupBox("Settings")
        settings = self.get_current_settings()

        self.setting_boxs = []
        layout = QGridLayout()
        i = 0
        j = 0
        for field, setting in zip(fields, settings):
            command, starting_value = setting

            label = QLabel(field)
            value_box = QDoubleSpinBox(minimum=-2000, maximum=2000)
            value_box.setValue(starting_value)

            self.setting_boxs.append([field, command, starting_value, value_box])

            if j % 2 == 0:
                layout.addWidget(label, i, 0)
                layout.addWidget(value_box, i, 1, 1, 2)
            else:
                layout.addWidget(label, i, 3)
                layout.addWidget(value_box, i, 4, 1, 2)
                i += 1

            j += 1

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.update_settings)
        layout.addWidget(apply_button, i+1, 0, 1, 6)
        self.settings_group.setLayout(layout)

    def update_settings(self):
        changes = []
        for box in self.setting_boxs:
            field, command, starting_value, spin_box = box

            current_value = spin_box.value()
            if current_value != starting_value:
                self.ser.write(f'{command}={current_value}\n'.encode())
                changes.append(f"({field}):\t {starting_value} ------> {current_value}")

        alert = QMessageBox()
        alert.setWindowTitle("Changes Applied")

        if changes:
            alert.setText("Changes")
            alert.setInformativeText("\n".join(changes))
        else:
            alert.setText("No Changes Made")

        alert.exec_()

    def get_current_settings(self):
        # Clear serial
        while self.ser.readline().decode():
            pass

        # Get current settings
        self.ser.write('$$\n'.encode())
        responses = []
        text = self.ser.readline().decode()
        while text:
            responses.append(text)
            text = self.ser.readline().decode()

        # Extract settings
        values = []
        for response in responses:
            if "=" in response:
                response = response.split("=")
                command = response[0]
                value = float(response[1].split(" ")[0])
                values.append([command, value])
            else:
                continue

        return values

class Sorting_Pill_Dialog(QWidget):
    def __init__(self,ser_grbl, ser_uno, pills, gcode):
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

        layout.addWidget(self.text,0,0)
        layout.addWidget(self.resume_pause,1,0,2,2)
        layout.addWidget(self.abort,1,2,2,2)
        layout.addWidget(self.description_box,3,0,2,4)
        layout.addWidget(self.progress_bar,5,0,1,4)


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
        self.worker = Sorting_Worker(self.ser_grbl,self.pills,self.gcode)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.sort_and_update)
        self.worker.progress.connect(self.update_description)
        self.worker.finished.connect(self.final_dialog)
        self.thread.start()

    # Updates the description field
    def update_description(self,nums):
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


    def closeEvent(self,event):
        self.timer.stop()
        event.accept()

class Serial_Reader(QObject):
    progress = pyqtSignal(str)
    update = pyqtSignal()

    def __init__(self, serial_port):
        super().__init__()
        self.ser = serial_port

    def update_display(self):
        if self.ser is not None:

            t = 0
            while True:
                text = self.ser.readline().decode('ascii')
                if text:
                    self.progress.emit(text)
                    self.update.emit()

class Sorting_Worker(QObject):
    progress = pyqtSignal(object)
    finished = pyqtSignal()

    def __init__(self,serial_port,pills,gcode):
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



    def set_sorting(self,state):
        self._sorting = state


def main():
    user_info = [{"id": "1234",
                  "first_name": 'John',
                  "last_name": "Smith",
                  "age": "72",
                  "address": "96 Whooovile RD KT",
                  "prescription": {"Advil": 2, "Motrin": 3},
                  "frequency" : [1,1],
                  "days_of_week": [[1,0,1,0,0,0,0],[1,0,1,0,1,0,0]]
                  }, {"id": "1281",
                      "first_name": 'Jan',
                      "last_name": "Doe",
                      "age": "65",
                      "address": "12 Seuss Valley MO",
                      "prescription": {"Benadryl": 2, "Motrin": 6},
                      "frequency": [2,2],
                      "days_of_week": [[1,0,0,0,0,0,0],[0,1,0,0,1,0,1]]
                      }]
    ui = Pill_Sorting_Interface(user_info)


if __name__ == "__main__":
    main()
