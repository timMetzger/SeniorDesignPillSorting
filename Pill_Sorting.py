# By: Timothy Metzger
from PyQt5.QtWidgets import (QApplication, QLabel, QProgressBar, QPushButton, QTableView, QWidget,
                             QHBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLineEdit, QVBoxLayout,
                             QHeaderView, QMenuBar, QActionGroup, QAction, QMessageBox, QSpinBox, QPlainTextEdit, QFrame)

from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon
from PyQt5.QtCore import Qt, QSortFilterProxyModel, QObject, QThread
import serial
import serial.tools.list_ports
from functools import partial


class Pill_Sorting_Interface():
    def __init__(self, scripts):
        self.app = QApplication([])
        self.scripts = scripts
        self.ser = None
        self.configurator = None
        self.controller = None

        self.menu_bar = QMenuBar()

        self.create_table()
        self.create_top_right_window()
        self.create_bottom_right_window()
        self.create_progress_bar()
        self.create_menu_bar()

        self.window = QWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(self.menu_bar, 0, 0)
        main_layout.addWidget(self.left_window, 1, 0, 4, 3)
        main_layout.addWidget(self.top_right_window, 1, 3)
        main_layout.addWidget(self.bottom_right_window, 2, 3)
        main_layout.addWidget(self.progress_bar, 3, 3)
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

        self.app.exec()

    # Create table and table search field
    def create_table(self):
        self.left_window = QGroupBox("Open Prescriptions")

        self.model = QStandardItemModel(len(self.scripts), len(self.scripts[0]) - 1)
        self.model.setHorizontalHeaderLabels(["ID", "First Name", "Last Name", "Age", "Address"])

        for i, user in enumerate(self.scripts):
            for j, key in enumerate(user.keys()):
                if key != "prescription":
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

    # Creates start,pause,abort button field
    def create_bottom_right_window(self):
        self.bottom_right_window = QGroupBox("Controls")

        self.start_button = QPushButton("Start")
        self.start_button.setCheckable(True)
        self.start_button.setChecked(False)
        self.start_button.clicked.connect(self.start_sort)

        self.pause_button = QPushButton("Pause")
        self.pause_button.setCheckable(True)
        self.pause_button.setChecked(False)
        self.pause_button.clicked.connect(self.pause_sort)

        self.abort_button = QPushButton("Abort")
        self.abort_button.setCheckable(True)
        self.abort_button.setChecked(False)
        self.abort_button.clicked.connect(self.abort_sort)

        layout = QHBoxLayout()
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.abort_button)

        self.bottom_right_window.setLayout(layout)

    # Creates progress bar
    def create_progress_bar(self):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 10000)
        self.progress_bar.setValue(0)

    # Creates menu bar
    def create_menu_bar(self):
        self.menu_bar = QMenuBar()
        self.ports = self.menu_bar.addMenu("Ports")
        self.refresh_ports()

        tools = self.menu_bar.addMenu("Tools")
        tools.addAction("Configuration", self.start_configurator)
        tools.addAction("Direct Control", self.start_direct_control)

    def start_configurator(self):
        if self.ser is not None:
            if self.configurator is None and self.controller is None:
                self.configurator = Configurator_Interface()
            self.configurator.show()
        else:
            self.serial_not_set()

    def start_direct_control(self):
        if self.ser is not None:
            if self.controller is None and self.configurator is None:
                self.controller = Direct_Control_Interface(self.ser)
            self.controller.show()
        else:
            self.serial_not_set()

    # Update the available com ports
    def refresh_ports(self):
        current_ports = serial.tools.list_ports.comports()
        if len(current_ports) == 0:
            self.ports.clear()
            refresh = QAction("Refresh", self.ports)
            refresh.triggered.connect(self.refresh_ports)
            self.ports.addAction(refresh)
        else:

            available_ports = []

            for current_port in self.ports.actions():
                available_ports.append(current_port.text())

            new_ports = []
            for port in current_ports:
                if port.device not in available_ports:
                    new_ports.append(port.device)

            com_group = QActionGroup(self.ports)

            if len(new_ports) != 0:
                self.ports.clear()
                for new_port in new_ports:
                    action = QAction(new_port, self.ports, checkable=True)
                    action.triggered.connect(self.set_com_port)
                    self.ports.addAction(action)
                    com_group.addAction(action)

                refresh = QAction("Refresh", self.ports)
                refresh.triggered.connect(self.refresh_ports)
                self.ports.addAction(refresh)

                com_group.setExclusive(True)

    # Set the serial communication attribute
    def set_com_port(self):
        # This is inside of a try except block due to the MenuBar object not cooperating with being unchecked
        try:
            for i, port in enumerate(self.ports.actions()[:-1]):
                if port.isChecked():
                    self.ser = serial.Serial(port.text(), 115200, timeout=1)

        except serial.SerialException:
            self.ser = None
            for button in self.ports.actions()[:-1]:
                button.setChecked(False)

    # TODO progress bar control and alert windows to user
    def start_sort(self):
        if self.ser is not None:
            print('start')
            self.ser.write(b'S')
        else:
            self.serial_not_set()

    def pause_sort(self):

        if self.ser is not None:
            print('pause')
            self.ser.write(b'P')
            #print(self.ser.readline())
        else:
            self.serial_not_set()

    def abort_sort(self):

        if self.ser is not None:
            print('abort')
            self.ser.write(b'A')
        else:
            self.serial_not_set()

    def serial_not_set(self):
        msg = QMessageBox()
        msg.setWindowTitle("Missing Serial Port")
        msg.setText("Please set the COM port using the menu bar.")
        msg.setInformativeText(
            "If the COM port is not present and the machine is connected please try a different USB port.")
        msg.setIcon(QMessageBox.Critical)

        msg.exec_()

    # Updates the prescriptions information field
    def update_information(self, selected, deselected):
        try:
            item = selected.indexes()[0]
            script_info = self.scripts[item.row()]["prescription"]
            script_string = ""
            for key, val in script_info.items():
                script_string += f"{key}: {val}\n"

            self.top_right_window.setPlainText(script_string)
        except IndexError:
            print("IndexError")

class Direct_Control_Interface(QWidget):
    def __init__(self,ser=None):
        super().__init__()
        layout = QGridLayout()

        self.left_group = None
        self.serial_input_box = None
        self.serial_output_box = None
        self.ser = ser

        self.create_left_button_group()
        self.create_serial_input()
        self.create_serial_output()
        self.create_positioning_group()

        layout.addWidget(self.positioning_group,0,0,4,1)
        layout.addWidget(self.left_group, 0, 4, 2, 2)
        layout.addWidget(self.serial_input_box, 2, 4, 2, 2)
        layout.addWidget(self.serial_output_box, 0, 6, 4, 1)

        self.setWindowTitle("Direct Control")
        self.setWindowIcon(QIcon("Gear-icon"))
        self.setLayout(layout)

    def create_left_button_group(self):
        self.left_group = QGroupBox("Controls")
        layout = QGridLayout()

        # X Control Buttons
        plus_x10 = QPushButton("X +10")
        plus_x10.clicked.connect(partial(self.move_axis_aboslute, 'x', 10))
        minus_x10 = QPushButton("X -10")
        minus_x10.clicked.connect(partial(self.move_axis_aboslute, 'x', -10))

        plus_x1 = QPushButton("X +1")
        plus_x1.clicked.connect(partial(self.move_axis_aboslute, 'x', 1))
        minus_x1 = QPushButton("X -1")
        minus_x1.clicked.connect(partial(self.move_axis_aboslute, 'x', -1))

        plus_x001 = QPushButton("X +0.001")
        plus_x001.clicked.connect(partial(self.move_axis_aboslute, 'x', 0.001))
        minus_x001 = QPushButton("X -0.001")
        minus_x001.clicked.connect(partial(self.move_axis_aboslute, 'x', -0.001))

        # Y Control Buttons
        plus_y10 = QPushButton("Y +10")
        plus_y10.clicked.connect(partial(self.move_axis_aboslute, 'y', 10))
        minus_y10 = QPushButton("Y -10")
        minus_y10.clicked.connect(partial(self.move_axis_aboslute, 'y', -10))

        plus_y1 = QPushButton("Y +1")
        plus_y1.clicked.connect(partial(self.move_axis_aboslute, 'y', 1))
        minus_y1 = QPushButton("Y -1")
        minus_y1.clicked.connect(partial(self.move_axis_aboslute, 'y', -1))

        plus_y001 = QPushButton("Y +0.001")
        plus_y001.clicked.connect(partial(self.move_axis_aboslute, 'y', 0.001))
        minus_y001 = QPushButton("Y -0.001")
        minus_y001.clicked.connect(partial(self.move_axis_aboslute, 'y', -0.001))

        # Z Control Buttons
        plus_z10 = QPushButton("Z +10")
        plus_z10.clicked.connect(partial(self.move_axis_aboslute, 'z', 10))
        minus_z10 = QPushButton("Z -10")
        minus_z10.clicked.connect(partial(self.move_axis_aboslute, 'z', -10))

        plus_z1 = QPushButton("Z +1")
        plus_z1.clicked.connect(partial(self.move_axis_aboslute, 'z', 1))
        minus_z1 = QPushButton("Z -1")
        minus_z1.clicked.connect(partial(self.move_axis_aboslute, 'z', -1))

        plus_z001 = QPushButton("Z +0.001")
        plus_z001.clicked.connect(partial(self.move_axis_aboslute, 'z', 0.001))
        minus_z001 = QPushButton("Z -0.001")
        minus_z001.clicked.connect(partial(self.move_axis_aboslute, 'z', -0.001))

        # User input control
        x_spinner_label = QLabel("X")
        x_spinner = QSpinBox(minimum=0, maximum=100)

        y_spinner_label = QLabel("Y")
        y_spinner = QSpinBox(minimum=0, maximum=100)

        z_spinner_label = QLabel("Z")
        z_spinner = QSpinBox(minimum=0, maximum=100)

        send_button = QPushButton("Send")
        send_button.clicked.connect(partial(self.move_to, [x_spinner.value(), y_spinner.value(), z_spinner.value()]))

        horizontal_separator = QFrame()
        horizontal_separator.setGeometry(60,110,751,20)
        horizontal_separator.setFrameShape(QFrame.HLine)
        horizontal_separator.setFrameShadow(QFrame.Sunken)

        vertical_separator1 = QFrame()
        vertical_separator1.setGeometry(60,110,751,20)
        vertical_separator1.setFrameShape(QFrame.VLine)
        vertical_separator1.setFrameShadow(QFrame.Sunken)

        vertical_separator2 = QFrame()
        vertical_separator2.setGeometry(60,110,751,20)
        vertical_separator2.setFrameShape(QFrame.VLine)
        vertical_separator2.setFrameShadow(QFrame.Sunken)

        # Group Buttons
        # Independent axis control buttons
        layout.addWidget(plus_x10, 0, 0, 1, 4)
        layout.addWidget(minus_x10, 0, 4, 1, 4)
        layout.addWidget(plus_x1,1,0,1,4)
        layout.addWidget(minus_x1,1,4,1,4)
        layout.addWidget(plus_x001,2,0,1,4)
        layout.addWidget(minus_x001,2,4,1,4)

        layout.addWidget(vertical_separator1,0,9,3,1)

        layout.addWidget(plus_y10,0,10,1,4)
        layout.addWidget(minus_y10,0,14,1,4)
        layout.addWidget(plus_y1,1,10,1,4)
        layout.addWidget(minus_y1,1,14,1,4)
        layout.addWidget(plus_y001,2,10,1,4)
        layout.addWidget(minus_y001,2,14,1,4)

        layout.addWidget(vertical_separator2,0,19,3,1)

        layout.addWidget(plus_z10,0,20,1,4)
        layout.addWidget(minus_z10,0,24,1,4)
        layout.addWidget(plus_z1,1,20,1,4)
        layout.addWidget(minus_z1,1,24,1,4)
        layout.addWidget(plus_z001,2,20,1,4)
        layout.addWidget(minus_z001,2,24,1,4)

        layout.addWidget(horizontal_separator,4,0,1,28)

        layout.addWidget(x_spinner_label,5,0)
        layout.addWidget(x_spinner,5,1,1,6)
        layout.addWidget(y_spinner_label,5,7)
        layout.addWidget(y_spinner,5,8,1,6)
        layout.addWidget(z_spinner_label,5,14)
        layout.addWidget(z_spinner,5,15,1,6)
        layout.addWidget(send_button,5,21,1,7)

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

        layout = QVBoxLayout()
        layout.addWidget(self.serial_output_field)
        self.serial_output_box.setLayout(layout)

        self.thread = QThread()
        self.worker = Serial_Reader(self.ser,self.serial_output_field)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.update_display)
        self.thread.start()

    def create_positioning_group(self):
        self.positioning_group = QGroupBox("Configure Positions")
        layout = QGridLayout()

        set_home_button = QPushButton("Set Home")
        set_home_button.clicked.connect(partial(self.set_pos, 0))
        move_button = QPushButton("Move Home")
        move_button.clicked.connect(partial(self.move_pos, 0))
        layout.addWidget(set_home_button, 0, 0, 1, 4)
        layout.addWidget(move_button, 0, 4, 1, 4)

        for i in range(0,12,2):
            set_button = QPushButton(f"Set P{i//2}")
            set_button.clicked.connect(partial(self.set_pos,i//2))
            move_button = QPushButton(f"Move P{i//2}")
            move_button.clicked.connect(partial(self.move_pos,i//2))



            layout.addWidget(set_button,i,0,1,4)
            layout.addWidget(move_button,i,4,1,4)
            if i != 10:
                horizontal_separator = QFrame()
                horizontal_separator.setGeometry(60, 110, 751, 20)
                horizontal_separator.setFrameShape(QFrame.HLine)
                horizontal_separator.setFrameShadow(QFrame.Sunken)
                layout.addWidget(horizontal_separator,i+1,0,1,8)

        self.positioning_group.setLayout(layout)

    def move_pos(self,pos):
        #TODO move to preset pos
        pass

    def set_pos(self,pos):
        #TODO set position number to coords given by grbl
        pass

    def move_axis_aboslute(self, axis, dist):
        pass
            #TODO Write statement to serial here

    def move_to(self, pos):
        pass
            #TODO Write statement to serial here

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


class Configurator_Interface(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()

        self.setWindowTitle("Machine Configuration Tool")
        self.setLayout(layout)

class Serial_Reader(QObject):
    def __init__(self,serial_port,display_field):
        super().__init__()
        self.ser = serial_port
        self.display = display_field

    def update_display(self):
        if self.ser is not None:
            t = 0
            while True:
                    text = self.ser.readline().decode('ascii')
                    if text:
                        self.display.appendPlainText(text)






def main():
    user_info = [{"id": "1234",
                  "first_name": 'John',
                  "last_name": "Smith",
                  "age": "72",
                  "address": "96 Whooovile RD KT",
                  "prescription": {"Advil": 2, "Motrin": 3}
                  }, {"id": "1281",
                      "first_name": 'Jan',
                      "last_name": "Doe",
                      "age": "65",
                      "address": "12 Seuss Valley MO",
                      "prescription": {"Benadryl": 2, "Motrin": 6}
                      }]
    ui = Pill_Sorting_Interface(user_info)


if __name__ == "__main__":
    main()
