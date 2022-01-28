# By: Timothy Metzger
from PyQt5.QtWidgets import (QApplication, QLabel, QProgressBar, QPushButton, QTableView, QWidget,
                             QHBoxLayout, QGroupBox, QGridLayout, QTextEdit, QLineEdit, QVBoxLayout, QHeaderView)

from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtCore import Qt, QSortFilterProxyModel


class Pill_Sorting_Interface():
    def __init__(self, scripts):
        self.app = QApplication([])
        self.scripts = scripts

        self.create_table()
        self.create_top_right_window()
        self.create_bottom_right_window()
        self.create_progress_bar()

        self.window = QWidget()

        main_layout = QGridLayout()
        main_layout.addWidget(self.left_window, 0, 0, 4, 3)
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

    # TODO progress bar control and alert windows to user
    def start_sort(self):
        print('start')

    def pause_sort(self):
        print('pause')

    def abort_sort(self):
        print('abort')

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
