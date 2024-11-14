import sys
import json
import yaml
import cv2
import torch
import numpy as np
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsRectItem, QVBoxLayout, QWidget, QGraphicsTextItem, QPushButton, QListWidget,
    QFileDialog, QHBoxLayout, QDialog
)
from PyQt6.QtGui import QPixmap, QPen, QColor, QPainter, QFont
from PyQt6.QtCore import Qt, QRectF, QPointF
from pathlib import Path
from typing import List

from loguru import logger

from browser.browser_env import PlaywrightBrowserEnv
from fsm import WebState
from project.manager import ProjectManager
from project.metadata import ProjectMetadata
from ui.open_project_input_dialog import OpenProjectInputDialog
from utils.image_util import pil_image_to_qpixmap
from web_parser.utils import annotate, annotate_processed_data


class ResizableRect(QGraphicsRectItem):
    def __init__(self, rect, label_text):
        super().__init__(rect)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.label_text = label_text
        self.setPen(QPen(QColor(0, 255, 0), 2))

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setPen(Qt.GlobalColor.red)
        font = QFont()
        font.setPointSize(8)  # Set smaller font size for annotation text
        painter.setFont(font)
        painter.drawText(self.rect().bottomLeft() + QPointF(0, 15), self.label_text)

class ImageWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Labeling Tool")
        self.showFullScreen()  # Set window to full screen

        # Initialize components
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.list_widget = QListWidget()
        self.save_button = QPushButton("Save Data")
        self.open_button = QPushButton("Open Project")
        self.annotate_button = QPushButton("Annotate and Save")  # New button for annotation

        # Left layout for the image, occupying more space
        self.image_layout = QVBoxLayout()
        self.image_layout.addWidget(self.view)

        # Right layout for list and buttons with smaller proportion
        self.control_layout = QVBoxLayout()
        self.control_layout.addWidget(self.open_button)
        self.control_layout.addWidget(self.save_button)
        self.control_layout.addWidget(self.annotate_button)
        self.control_layout.addWidget(self.list_widget)

        # Main layout (horizontal) with image on the left and controls on the right
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.image_layout, 3)  # 3/4 of the width for image view
        self.main_layout.addLayout(self.control_layout, 1)  # 1/4 for controls

        container = QWidget()
        container.setLayout(self.main_layout)
        self.setCentralWidget(container)

        # Connect buttons
        self.open_button.clicked.connect(self.load_yaml)
        self.save_button.clicked.connect(self.save_data)
        self.annotate_button.clicked.connect(self.annotate_and_save_image)  # Connect annotate button
        self.list_widget.itemClicked.connect(self.display_selected_item)

        # Variables to hold data
        self.data = None
        # self.current_image_path = ""
        self.current_image = None

        self.current_label_data = {}
        self.current_parsed_content = {}

        browser = PlaywrightBrowserEnv()
        self.browser = browser
        self.browser.start_browser_sync()

        self.selected_state: WebState = None
        self.project_manager: ProjectManager = None

    def load_yaml(self):
        dialog = OpenProjectInputDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        project_path = dialog.path_input.text()

        logger.info(f"New Project Created:\n "
                    f"Path: {project_path} \n")

        metadata = ProjectMetadata(project_path)

        # load project
        self.project_manager = ProjectManager(metadata, self.browser)
        self.project_manager.load_project()

        self.project_manager.fsm_graph.current_state = self.project_manager.fsm_graph.root_state

        self.list_widget.clear()
        self.states = self.project_manager.fsm_graph.states

        for k in self.states:
            print(k)
            self.list_widget.addItem(k)


    def display_selected_item(self, item):
        # Clear previous scene items
        self.scene.clear()

        selected_state: WebState = self.states[item.text()]
        self.selected_state = selected_state

        # Load image
        self.current_image = selected_state.web_image
        self.current_label_data = selected_state.label_coordinates
        self.current_parsed_content = selected_state.parsed_content

        self.pixmap = pil_image_to_qpixmap(self.current_image)
        self.image_item = QGraphicsPixmapItem(self.pixmap)
        self.scene.addItem(self.image_item)

        # Draw labels
        for key, coordinates in self.current_label_data.items():
            x, y, w, h = coordinates
            text = self.current_parsed_content[int(key)]
            rect_item = ResizableRect(QRectF(x, y, w, h), f"{key}: {text}")
            self.scene.addItem(rect_item)

    def annotate_and_save_image(self):
        # Load image
        image_source = np.array(self.current_image)

        # Prepare data for annotation
        boxes = torch.tensor([self.current_label_data[key] for key in self.current_label_data])  # Example bounding boxes
        boxes[:, 2] = boxes[:, 0] + boxes[:, 2]  # x2 = x + w
        boxes[:, 3] = boxes[:, 1] + boxes[:, 3]


        logits = torch.ones(len(self.current_label_data))  # Dummy logits
        # phrases = list(self.current_parsed_content.values())  # Labels for bounding boxes
        phrases = list(self.current_parsed_content)

        text_scale = 0.3  # Example text scale for annotation

        # Call the annotate function
        annotated_image, label_coordinates = annotate_processed_data(
            image_source=image_source,
            boxes=boxes,
            logits=logits,
            phrases=phrases,
            text_scale=text_scale
        )

        pil_image = Image.fromarray(annotated_image)
        # pil_image.show()


        self.selected_state.som_image = pil_image

        print(f"Annotated image and Save")

    def save_data(self):
        # updated_data = []
        # formatted_data = {}

        updated_coordinates = {}
        for item in self.scene.items():
            if isinstance(item, ResizableRect):
                rect = item.sceneBoundingRect()
                box_id = item.label_text.split(":")[0]
                updated_coordinates[box_id] = [rect.x(), rect.y(), rect.width(), rect.height()]
        self.selected_state.label_coordinates = updated_coordinates

        self.annotate_and_save_image()

        self.project_manager.save_project()

        # for uuid in self.data:
        #     entry = self.data[uuid]
        #     if entry["image_path"] == self.current_image_path:
        #         updated_coordinates = {}
        #         for item in self.scene.items():
        #             if isinstance(item, ResizableRect):
        #                 # rect = item.rect()
        #                 rect = item.sceneBoundingRect()
        #                 box_id = item.label_text.split(":")[0]
        #                 updated_coordinates[box_id] = [rect.x(), rect.y(), rect.width(), rect.height()]
        #         entry["label_coordinates"] = json.dumps(updated_coordinates)
        #
        #         self.selected_state.label_coordinates = json.loads(updated_coordinates)

        #     updated_data.append(entry)
        #
        #     formatted_data[entry["id"]] = entry
        #
        # # Save updated data to a new file
        # with open("updated_data.yaml", "w") as f:
        #     yaml.dump(formatted_data, f)

        print("Data saved")


def main():
    app = QApplication(sys.argv)
    window = ImageWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

