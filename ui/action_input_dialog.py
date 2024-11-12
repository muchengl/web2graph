
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

        self.text_edit = QPlainTextEdit(self)
        self.text_edit.setPlaceholderText("Action content (for type only)")

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.prompt_label)
        layout.addWidget(QLabel("Action Type:"))
        layout.addWidget(self.action_combo_box)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

    def get_data(self):
        selected_action = self.action_combo_box.currentText()
        input_text = self.text_edit.toPlainText()
        return selected_action, input_text

