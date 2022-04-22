import configparser

import serial
import serial.tools.list_ports
from PyQt5.QtCore import QSortFilterProxyModel, Qt
from PyQt5.QtGui import QIcon, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QApplication, QMenuBar, QWidget, QGridLayout, QGroupBox, QLineEdit, QHBoxLayout, QLabel, \
    QTableView, QHeaderView, QVBoxLayout, QTextEdit, QPushButton, QMessageBox, QCheckBox

from Sorting_Timed_Message import SortingMessageBox
from Sorting_Pill_Dialog import Sorting_Pill_Dialog
from Configuration_Interface import Configuration_Interface
from Direct_Control_Interface import Direct_Control_Interface


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
            # self.create_progress_bar()
            self.create_menu_bar()

            self.window = QWidget()

            main_layout = QGridLayout()
            main_layout.addWidget(self.menu_bar, 0, 0)
            main_layout.addWidget(self.left_window, 1, 0, 4, 3)
            main_layout.addWidget(self.top_right_window, 1, 3)
            main_layout.addWidget(self.bottom_right_window, 2, 3)
            # main_layout.addWidget(self.progress_bar, 3, 3)
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
        layout.addWidget(self.scan_rfid_button, 0, 0, 1, 3)
        layout.addWidget(self.start_button, 1, 0, 1, 3)

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
        self.controller = Direct_Control_Interface(self.ser_grbl)
        self.controller.show()

        self.controller = None

    def start_sorter(self,steps = False):
        self.sorter = Sorting_Pill_Dialog(self.ser_grbl, self.ser_uno, self.current_selection['prescription'],
                                              self.gcode,steps)
        self.sorter.show()

        self.sorter = None

    # Set the serial communication attribute
    def set_com_ports(self):
        ports = serial.tools.list_ports.comports()
        for i, port in enumerate(ports):
            print(port.description)
            if port.description.startswith("Arduino"): # tty for linux
                self.ser_uno = serial.Serial(port=port.device, baudrate=115200, timeout=1)
            elif port.description.startswith("USB"):
                self.ser_grbl = serial.Serial(port=port.device, baudrate=115200, timeout=1)
                self.ser_grbl.write('$X\n'.encode())

    # Display messagebox that serial ports are not connected
    def serial_not_set(self):
        msg = QMessageBox()
        msg.setWindowTitle("Missing Serial Port")
        msg.setText("Please connect both USBs")
        msg.setInformativeText(
            "If both USBs are connected and you are still getting this error please try different ports")
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

            check_box = QCheckBox("Step by Step?")

            msg = QMessageBox()
            msg.setWindowTitle("Load Medication")
            msg.setText("Please load medication")
            msg.setInformativeText(self.current_selection_string)
            msg.setIcon(QMessageBox.Information)
            msg.setCheckBox(check_box)

            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            response = msg.exec_()
            inSteps = check_box.isChecked()

            if response == QMessageBox.Ok:
                self.generate_gcode()
                starting_msg = SortingMessageBox(timeout=5)
                starting_msg.exec_()
                self.start_sorter(inSteps)
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
            script_string += "-" * 30 + "\n"
            i = 1
            for key, val in script_info.items():
                script_string += f"Slot {i}".ljust(15) + f"{key}: {val}".ljust(20) + "\n"
                i += 1

            self.current_selection_string = script_string
            self.top_right_window.setPlainText(script_string)
        except IndexError:
            print("IndexError")

    # Generate the gcode commands for sorting
    def generate_gcode(self):
        config = configparser.ConfigParser()
        config.read(self.config)

        home = config['POSITIONS']['Home']
        safe = config['POSITIONS']['Safe']
        p1_x = float(config['POSITIONS']['P1'].split(" ")[0][1:])
        p2_x = float(config['POSITIONS']['P2'].split(" ")[0][1:])

        p3_y = float(config['POSITIONS']['P3'].split(" ")[1][1:])
        p4_y = float(config['POSITIONS']['P4'].split(" ")[1][1:])

        x_gap = p2_x - p1_x
        y_gap = p4_y - p3_y

        self.gcode = []
        self.gcode.append('$X\n')
        self.gcode.append(f'G90 {safe}\n')



        # Sort a single medication type at a time
        current_slot = p1_x
        for i, val in enumerate(self.current_selection['prescription'].values()):

            # Get frequency and days of the week
            freq = self.current_selection['frequency'][i]
            days = [j for j, v in enumerate(self.current_selection['days_of_week'][i]) if v]

            for day in days:
                # Rotate sorted pill bin to appropriate day
                self.gcode.append(f'G90 Y{day*y_gap}\n')  # TODO this will need tweaking

                # Drop freq number of pills in the corresponding day
                for _ in range(freq):
                    self.gcode.append(f'G90 X{current_slot}\n')  # move to slot
                    self.gcode.append(f'M8\n')  # spindle on
                    self.gcode.append('G90 Z-5\n')  # descend
                    self.gcode.append('G90 Z0\n')  # ascend
                    self.gcode.append(f'G90 {home}\n')  # return to drop
                    self.gcode.append(f'M9\n')  # spindle off

            current_slot += x_gap