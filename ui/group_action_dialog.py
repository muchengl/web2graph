import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
    QDialogButtonBox, QHeaderView, QPushButton
)
from PyQt6.QtCore import Qt

from browser.actions import action_types


# Assume action_types is defined somewhere
# action_types = ['Type1', 'Type2', 'Type3']

class GroupActionDialog(QDialog):
    def __init__(self, actions):
        super().__init__()
        self.setWindowTitle("Action Dialog")

        # Set the default size of the dialog
        self.resize(800, 600)  # Adjust the width and height as needed

        self.actions = actions  # List of available actions

        # Action list at the top
        self.action_list_widget = QListWidget()
        self.action_list_widget.addItems(self.actions)
        self.action_list_widget.itemDoubleClicked.connect(self.add_action_to_waiting_list)

        # Waiting list (QTableWidget)
        self.waiting_list_widget = QTableWidget()
        self.waiting_list_widget.setColumnCount(5)  # Added a column for action_id
        self.waiting_list_widget.setHorizontalHeaderLabels(['Action Type', 'Action Content', 'Action Name', 'Action Info', 'Action ID'])
        self.waiting_list_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.waiting_list_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.waiting_list_widget.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        # Hide the 'Action ID' column
        self.waiting_list_widget.setColumnHidden(4, True)

        # Remove Selected button
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_selected_action)

        # Dialog buttons (OK and Cancel)
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout setup
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Available Actions:"))
        main_layout.addWidget(self.action_list_widget)
        main_layout.addWidget(QLabel("Waiting List:"))
        main_layout.addWidget(self.waiting_list_widget)

        # Add the Remove button and Dialog buttons to a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.remove_button)
        button_layout.addStretch()
        button_layout.addWidget(self.button_box)

        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

    def add_action_to_waiting_list(self, item):
        # Get the action name and its index (id)
        action_name = item.text()
        action_id = self.action_list_widget.row(item)

        # Add a new row to the waiting list
        row = self.waiting_list_widget.rowCount()
        self.waiting_list_widget.insertRow(row)

        # Action Type (ComboBox)
        combo = QComboBox()
        combo.addItems(action_types)
        self.waiting_list_widget.setCellWidget(row, 0, combo)

        # Action Content (LineEdit)
        content_edit = QLineEdit()
        self.waiting_list_widget.setCellWidget(row, 1, content_edit)

        # Action Name (LineEdit), default value is action_name
        name_edit = QLineEdit(action_name)
        self.waiting_list_widget.setCellWidget(row, 2, name_edit)

        # Action Info (LineEdit)
        info_edit = QLineEdit()
        self.waiting_list_widget.setCellWidget(row, 3, info_edit)

        # Action ID (QTableWidgetItem), hidden
        id_item = QTableWidgetItem(str(action_id))
        self.waiting_list_widget.setItem(row, 4, id_item)

    def remove_selected_action(self):
        # Get the selected rows
        selected_rows = self.waiting_list_widget.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            self.waiting_list_widget.removeRow(index.row())

    def get_waiting_list_data(self):
        data = []
        for row in range(self.waiting_list_widget.rowCount()):
            # Get widgets from the cells
            combo = self.waiting_list_widget.cellWidget(row, 0)
            action_type = combo.currentText() if combo else ''

            content_edit = self.waiting_list_widget.cellWidget(row, 1)
            action_content = content_edit.text() if content_edit else ''

            name_edit = self.waiting_list_widget.cellWidget(row, 2)
            action_name = name_edit.text() if name_edit else ''

            info_edit = self.waiting_list_widget.cellWidget(row, 3)
            action_info = info_edit.text() if info_edit else ''

            # Get the hidden action_id
            id_item = self.waiting_list_widget.item(row, 4)
            action_id = int(id_item.text()) if id_item else -1

            action_data = {
                'action_type': action_type,
                'action_content': action_content,
                'action_name': action_name,
                'action_info': action_info,
                'action_id': action_id
            }
            data.append(action_data)
        return data

if __name__ == '__main__':
    app = QApplication(sys.argv)

    actions = ['Action1', 'Action2', 'Action3']  # Sample actions
    dialog = GroupActionDialog(actions)
    if dialog.exec():
        waiting_list_data = dialog.get_waiting_list_data()
        print(waiting_list_data)  # Output the data from the waiting list
    else:
        print("Dialog canceled.")

    sys.exit()
