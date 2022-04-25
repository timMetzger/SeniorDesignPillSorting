from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QGridLayout, QGroupBox, QLabel, QDoubleSpinBox, QPushButton, QMessageBox


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
        self.setAttribute(Qt.WA_DeleteOnClose)

    def create_fields(self):
        fields = ["Step Pulse", "Step Idle Delay", "Step Port Invert Mask", "Dir Port Invert Mask",
                  "Step Enable Invert", "Limit Pins Invert",
                  "Probe Pin Invert", "Status Report Mask", "Junction Deviation", "Arc Tolerance", "Report Inches",
                  "Soft Limits", "Hard Limits",
                  "Homing Cycle", "Homing Dir Invert Mask", "Homing Feed", "Homing Seek", "Homing Debounce",
                  "Homing Pull-Off", "X Step/mm", "Y Step/mm", "Z Step/mm",
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
        layout.addWidget(apply_button, i + 1, 0, 1, 6)
        self.settings_group.setLayout(layout)

    def update_settings(self):
        changes = []
        for i, box in enumerate(self.setting_boxs):
            field, command, starting_value, spin_box = box

            current_value = spin_box.value()
            if current_value != starting_value:
                print(f'{command}={current_value}\n')
                self.ser.write(f'{command}={current_value}\n'.encode())
                changes.append(f"({field}):\t {starting_value} ---> {current_value}")
                self.setting_boxs[i][2] = current_value

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

        return values

    def closeEvent(self, event):
        event.accept()