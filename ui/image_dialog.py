from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap
import sys


class ImageDialog(QDialog):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Current Webpage")

        layout = QVBoxLayout()

        label = QLabel(self)
        pixmap = QPixmap(image_path)
        label.setPixmap(pixmap)

        layout.addWidget(label)

        close_button = QPushButton("Close", self)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)


def show_image_dialog(image_path):
    app = QApplication(sys.argv)
    dialog = ImageDialog(image_path)
    dialog.exec()

