
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QDialog, QVBoxLayout, QPlainTextEdit, QMessageBox, \
    QDialogButtonBox, QLabel, QComboBox

from browser.actions import action_types


class ActionInputBox(QDialog):
    def __init__(self, prompt_message):
        super().__init__()
        self.setWindowTitle("Action")

        self.prompt_label = QLabel(prompt_message, self)

        self.action_combo_box = QComboBox(self)
        self.action_combo_box.addItems(action_types)

        self.action_content = QPlainTextEdit(self)
        self.action_content.setPlaceholderText("Action content (for type only)")

        self.name = QPlainTextEdit(self)
        self.name.setPlaceholderText("Action name")

        self.info = QPlainTextEdit(self)
        self.info.setPlaceholderText("Add a description for this action")

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.prompt_label)
        layout.addWidget(QLabel("Action Type:"))
        layout.addWidget(self.action_combo_box)

        layout.addWidget(self.action_content)
        layout.addWidget(self.name)
        layout.addWidget(self.info)

        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_data(self):
        selected_action = self.action_combo_box.currentText()
        action_content = self.action_content.toPlainText()
        action_name = self.name.toPlainText()
        action_info = self.info.toPlainText()

        return selected_action, action_content,action_name, action_info

