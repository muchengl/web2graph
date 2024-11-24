# import sys
# from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
# from PyQt6.QtGui import QPixmap, QPainter, QPen
# from PyQt6.QtWidgets import (
#     QApplication,
#     QDialog,
#     QVBoxLayout,
#     QLabel,
#     QPushButton,
#     QHBoxLayout,
#     QFormLayout,
#     QDialogButtonBox,
#     QListWidget,
#     QListWidgetItem,
#     QLineEdit,
#     QScrollArea,
# )
# from PIL.ImageQt import ImageQt
# from PIL import Image
#
#
# class ImageLabel(QLabel):
#     rectangles_changed = pyqtSignal()  # Signal to notify when rectangles change
#
#     def __init__(self):
#         super().__init__()
#         self.start_point = None
#         self.end_point = None
#         self.drawing = False
#         self.rectangles = []  # Stores (QRect, ID, metadata)
#         self.selected_rect_index = None  # Index of the selected rectangle
#
#     # def set_rectangles_from_data(self, rectangles_data):
#     #     """Set rectangles from a list of rectangle data."""
#     #     self.rectangles = []
#     #     for rect_data in rectangles_data:
#     #         coords = rect_data['coordinates']
#     #         rect_id = rect_data.get('id', 'Unset')
#     #         metadata = rect_data.get('metadata', '')
#     #         rect = QRect(QPoint(int(coords[0]), int(coords[1])), QPoint(int(coords[2]), int(coords[3])))
#     #         self.rectangles.append((rect, rect_id, metadata))
#     #     self.rectangles_changed.emit()
#     #     self.update()
#
#     def set_rectangles_from_data(self, rectangles_data):
#         """Set rectangles from a list of rectangle data."""
#         self.rectangles = []
#         for rect_data in rectangles_data:
#             x, y, w, h = rect_data['coordinates']
#             rect_id = rect_data.get('id', 'Unset')
#             metadata = rect_data.get('metadata', '')
#             rect = QRect(int(x), int(y), int(w), int(h))
#             self.rectangles.append((rect, rect_id, metadata))
#         self.rectangles_changed.emit()
#         self.update()
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton:
#             click_point = event.position().toPoint()
#             # Check if click is inside any rectangle
#             for idx, (rect, rect_id, metadata) in enumerate(self.rectangles):
#                 if rect.contains(click_point):
#                     self.selected_rect_index = idx
#                     self.rectangles_changed.emit()
#                     self.update()
#                     return
#             # If not inside any rectangle, start drawing a new one
#             self.start_point = click_point
#             self.end_point = click_point
#             self.drawing = True
#             self.selected_rect_index = None  # Deselect any selected rectangle
#             self.rectangles_changed.emit()
#             self.update()
#
#     def mouseMoveEvent(self, event):
#         if self.drawing:
#             self.end_point = event.position().toPoint()
#             self.update()
#
#     def mouseReleaseEvent(self, event):
#         if event.button() == Qt.MouseButton.LeftButton and self.drawing:
#             self.end_point = event.position().toPoint()
#             rect = QRect(self.start_point, self.end_point).normalized()
#             self.rectangles.append((rect, "Unset", ""))  # Default ID is "Unset", metadata is empty
#             self.drawing = False
#             self.selected_rect_index = len(self.rectangles) - 1  # Select the new rectangle
#             self.rectangles_changed.emit()
#             self.update()
#
#     def paintEvent(self, event):
#         super().paintEvent(event)
#         if self.pixmap() is None:
#             return
#         painter = QPainter(self)
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#         pen = QPen(Qt.GlobalColor.red, 2)
#         painter.setPen(pen)
#         for idx, (rect, rect_id, metadata) in enumerate(self.rectangles):
#             if idx == self.selected_rect_index:
#                 pen.setColor(Qt.GlobalColor.blue)
#                 pen.setWidth(3)
#                 painter.setPen(pen)
#             else:
#                 pen.setColor(Qt.GlobalColor.red)
#                 pen.setWidth(2)
#                 painter.setPen(pen)
#             painter.drawRect(rect)
#             painter.drawText(rect.topLeft() + QPoint(5, 15), f"{rect_id}")
#         if self.drawing and self.start_point and self.end_point:
#             pen.setColor(Qt.GlobalColor.green)
#             pen.setWidth(2)
#             painter.setPen(pen)
#             temp_rect = QRect(self.start_point, self.end_point).normalized()
#             painter.drawRect(temp_rect)
#
#     # def get_rectangles(self):
#     #     return [
#     #         {
#     #             "id": rect_id,
#     #             "metadata": metadata,
#     #             "coordinates": [rect.topLeft().x(),
#     #                             rect.topLeft().y(),
#     #                             rect.bottomRight().x(),
#     #                             rect.bottomRight().y()],
#     #         }
#     #         for rect, rect_id, metadata in self.rectangles
#     #     ]
#
#     def get_rectangles(self):
#         return [
#             {
#                 "id": rect_id,
#                 "metadata": metadata,
#                 "coordinates": [rect.x(), rect.y(), rect.width(), rect.height()],
#             }
#             for rect, rect_id, metadata in self.rectangles
#         ]
#
#     def set_selected_rect_data(self, new_id, new_metadata):
#         if self.selected_rect_index is not None:
#             rect, _, _ = self.rectangles[self.selected_rect_index]
#             self.rectangles[self.selected_rect_index] = (rect, new_id, new_metadata)
#             self.rectangles_changed.emit()
#             self.update()
#
#
# class ImageEditorDialog(QDialog):
#     def __init__(self, pil_image, rectangles=None, parent=None):
#         super().__init__(parent)
#         self.setWindowTitle("Rectangle Image Editor")
#         self.showMaximized()
#
#         self.image_label = ImageLabel()
#         self.image_label.rectangles_changed.connect(self.update_rectangles_list)
#
#         # Convert PIL image to QPixmap
#         qimage = ImageQt(pil_image)
#         pixmap = QPixmap.fromImage(qimage)
#         self.image_label.setPixmap(pixmap)
#         self.image_label.setScaledContents(True)  # Ensure content scales properly
#
#
#         # Wrap the image label in a scrollable area
#         scroll_area = QScrollArea()
#         scroll_area.setWidgetResizable(True)  # Ensure scrolling adapts to the widget size
#         scroll_area.setWidget(self.image_label)
#
#         # Left-side layout for the image
#         image_layout = QVBoxLayout()
#         image_layout.addWidget(scroll_area)
#
#         # Right-side layout for the rectangles list and controls
#         controls_layout = QVBoxLayout()
#
#         # List widget to display rectangles
#         self.rectangles_list = QListWidget()
#         self.rectangles_list.itemClicked.connect(self.select_rectangle_from_list)
#         controls_layout.addWidget(self.rectangles_list)
#
#         # Form for rectangle ID and metadata input
#         form_layout = QFormLayout()
#         self.id_input = QLineEdit()
#         self.metadata_input = QLineEdit()
#         form_layout.addRow("Rectangle ID:", self.id_input)
#         form_layout.addRow("Metadata:", self.metadata_input)
#         controls_layout.addLayout(form_layout)
#
#         # Buttons for setting data and removing selected rectangle
#         self.set_data_button = QPushButton("Set ID and Metadata")
#         self.set_data_button.clicked.connect(self.set_rectangle_data)
#         self.remove_button = QPushButton("Remove Rectangle")
#         self.remove_button.clicked.connect(self.remove_selected_rectangle)
#
#         controls_layout.addWidget(self.set_data_button)
#         controls_layout.addWidget(self.remove_button)
#
#         # Add OK and Cancel buttons
#         button_box = QDialogButtonBox(
#             QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
#         )
#         button_box.accepted.connect(self.accept)
#         button_box.rejected.connect(self.reject)
#         controls_layout.addWidget(button_box)
#
#         # Combine left and right layouts
#         main_layout = QHBoxLayout()
#         main_layout.addLayout(image_layout, 2)  # Image takes more space
#         main_layout.addLayout(controls_layout, 1)
#
#         self.setLayout(main_layout)
#
#         # If rectangles are provided, set them
#         if rectangles is not None:
#             logger.info(f"load rectangles: {rectangles}")
#             self.image_label.set_rectangles_from_data(rectangles)
#             self.update_rectangles_list()
#
#     def update_rectangles_list(self):
#         """Update the list widget with the current rectangles."""
#         self.rectangles_list.clear()
#         for idx, (rect, rect_id, metadata) in enumerate(self.image_label.rectangles):
#             item = QListWidgetItem(
#                 f"Rect {idx + 1}: ID={rect_id}, Metadata={metadata}, "
#                 f"Coords=({rect.topLeft().x()}, {rect.topLeft().y()} -> "
#                 f"{rect.bottomRight().x()}, {rect.bottomRight().y()})"
#             )
#             self.rectangles_list.addItem(item)
#         # If a rectangle is selected in the image, select it in the list
#         if self.image_label.selected_rect_index is not None:
#             self.rectangles_list.setCurrentRow(self.image_label.selected_rect_index)
#             rect, rect_id, metadata = self.image_label.rectangles[self.image_label.selected_rect_index]
#             self.id_input.setText(rect_id)
#             self.metadata_input.setText(metadata)
#         else:
#             self.id_input.clear()
#             self.metadata_input.clear()
#
#     def select_rectangle_from_list(self, item):
#         """Select a rectangle from the list."""
#         index = self.rectangles_list.row(item)
#         self.image_label.selected_rect_index = index
#         rect, rect_id, metadata = self.image_label.rectangles[index]
#         self.id_input.setText(rect_id)
#         self.metadata_input.setText(metadata)
#         self.image_label.update()
#
#     def set_rectangle_data(self):
#         """Set the ID and metadata for the selected rectangle."""
#         new_id = self.id_input.text()
#         new_metadata = self.metadata_input.text()
#         if new_id:
#             self.image_label.set_selected_rect_data(new_id, new_metadata)
#             self.update_rectangles_list()
#
#     def remove_selected_rectangle(self):
#         """Remove the selected rectangle."""
#         if self.image_label.selected_rect_index is not None:
#             self.image_label.rectangles.pop(self.image_label.selected_rect_index)
#             self.image_label.selected_rect_index = None
#             self.update_rectangles_list()
#             self.image_label.update()
#
#     def get_configurations(self):
#         return self.image_label.get_rectangles()
#
#
# # Main view to invoke the dialog
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#
#     # Load a sample PIL image
#     pil_image = Image.new("RGB", (800, 600), "white")  # Example: a blank white image
#
#     # Create some sample rectangles in the format you described
#     sample_rectangles = [
#         {"id": "Rect1", "metadata": "Metadata1", "coordinates": [100, 100, 300, 250]},
#         {"id": "Rect2", "metadata": "Metadata2", "coordinates": [300, 250, 400, 350]},
#     ]
#
#     dialog = ImageEditorDialog(pil_image, rectangles=sample_rectangles)
#     if dialog.exec() == QDialog.DialogCode.Accepted:
#         configurations = dialog.get_configurations()
#         print("Rectangle configurations:")
#         for config in configurations:
#             print(config)
#
#     sys.exit(app.exec())

import sys
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QFormLayout,
    QDialogButtonBox,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QScrollArea,
)
from PIL.ImageQt import ImageQt
from PIL import Image


class ImageLabel(QLabel):
    rectangles_changed = pyqtSignal()  # Signal to notify when rectangles change

    def __init__(self):
        super().__init__()
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.rectangles = []  # Stores (QRect, ID, metadata)
        self.selected_rect_index = None  # Index of the selected rectangle
        self.action_mode = None  # 'drawing', 'moving', 'resizing', or None
        self.resize_direction = None  # Direction for resizing
        self.prev_point = None  # Previous mouse position

    def set_rectangles_from_data(self, rectangles_data):
        """Set rectangles from a list of rectangle data."""
        self.rectangles = []
        for rect_data in rectangles_data:
            x, y, w, h = rect_data['coordinates']
            rect_id = rect_data.get('id', 'Unset')
            metadata = rect_data.get('metadata', '')
            rect = QRect(int(x), int(y), int(w), int(h))
            self.rectangles.append((rect, rect_id, metadata))
        self.rectangles_changed.emit()
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            click_point = event.position().toPoint()
            self.prev_point = click_point

            # First, check if the click is near a corner for resizing
            for idx, (rect, rect_id, metadata) in enumerate(self.rectangles):
                corner = self.get_resize_direction(rect, click_point)
                if corner is not None:
                    # Start resizing
                    self.selected_rect_index = idx
                    self.action_mode = 'resizing'
                    self.resize_direction = corner
                    self.rectangles_changed.emit()
                    self.update()
                    return

            # Next, check if click is inside any rectangle for moving
            for idx, (rect, rect_id, metadata) in enumerate(self.rectangles):
                if rect.contains(click_point):
                    # Start moving
                    self.selected_rect_index = idx
                    self.action_mode = 'moving'
                    self.rectangles_changed.emit()
                    self.update()
                    return

            # If not near any rectangle or inside, start drawing a new one
            self.start_point = click_point
            self.end_point = click_point
            self.drawing = True
            self.action_mode = 'drawing'
            self.selected_rect_index = None  # Deselect any selected rectangle
            self.rectangles_changed.emit()
            self.update()

    def get_resize_direction(self, rect, point):
        """Check if the point is near any corner of the rectangle."""
        threshold = 10  # Pixels within which the resize handle is active
        resize_handles = {
            'top_left': rect.topLeft(),
            'top_right': rect.topRight(),
            'bottom_left': rect.bottomLeft(),
            'bottom_right': rect.bottomRight(),
        }
        for direction, handle_point in resize_handles.items():
            if (handle_point - point).manhattanLength() <= threshold:
                return direction
        return None

    def mouseMoveEvent(self, event):
        current_point = event.position().toPoint()
        if self.action_mode == 'drawing' and self.drawing:
            self.end_point = current_point
            self.update()
        elif self.action_mode == 'moving' and self.selected_rect_index is not None:
            delta = current_point - self.prev_point
            rect, rect_id, metadata = self.rectangles[self.selected_rect_index]
            rect.translate(delta)
            self.rectangles[self.selected_rect_index] = (rect, rect_id, metadata)
            self.prev_point = current_point
            self.rectangles_changed.emit()
            self.update()
        elif self.action_mode == 'resizing' and self.selected_rect_index is not None:
            rect, rect_id, metadata = self.rectangles[self.selected_rect_index]
            rect = self.resize_rect(rect, self.resize_direction, current_point)
            self.rectangles[self.selected_rect_index] = (rect.normalized(), rect_id, metadata)
            self.prev_point = current_point
            self.rectangles_changed.emit()
            self.update()

    def resize_rect(self, rect, direction, new_point):
        """Resize rectangle according to the drag direction and new point."""
        if direction == 'top_left':
            rect.setTopLeft(new_point)
        elif direction == 'top_right':
            rect.setTopRight(new_point)
        elif direction == 'bottom_left':
            rect.setBottomLeft(new_point)
        elif direction == 'bottom_right':
            rect.setBottomRight(new_point)
        return rect

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.action_mode == 'drawing' and self.drawing:
                self.end_point = event.position().toPoint()
                rect = QRect(self.start_point, self.end_point).normalized()
                self.rectangles.append((rect, "Unset", ""))  # Default ID is "Unset", metadata is empty
                self.drawing = False
                self.selected_rect_index = len(self.rectangles) - 1  # Select the new rectangle
                self.action_mode = None
                self.rectangles_changed.emit()
                self.update()
            elif self.action_mode in ('moving', 'resizing'):
                self.action_mode = None
                self.resize_direction = None
                self.prev_point = None
                self.rectangles_changed.emit()
                self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap() is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        for idx, (rect, rect_id, metadata) in enumerate(self.rectangles):
            if idx == self.selected_rect_index:
                pen.setColor(Qt.GlobalColor.blue)
                pen.setWidth(3)
                painter.setPen(pen)
            else:
                pen.setColor(Qt.GlobalColor.red)
                pen.setWidth(2)
                painter.setPen(pen)
            painter.drawRect(rect)
            painter.drawText(rect.topLeft() + QPoint(5, 15), f"{rect_id}")
            # If rectangle is selected, draw resize handles
            if idx == self.selected_rect_index:
                self.draw_resize_handles(painter, rect)
        if self.drawing and self.start_point and self.end_point:
            pen.setColor(Qt.GlobalColor.green)
            pen.setWidth(2)
            painter.setPen(pen)
            temp_rect = QRect(self.start_point, self.end_point).normalized()
            painter.drawRect(temp_rect)

    def draw_resize_handles(self, painter, rect):
        """Draw small squares at the corners of the rectangle for resizing."""
        handle_size = 6
        painter.setBrush(Qt.GlobalColor.white)
        painter.setPen(Qt.GlobalColor.black)
        handles = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
        ]
        for point in handles:
            handle_rect = QRect(
                point.x() - handle_size // 2,
                point.y() - handle_size // 2,
                handle_size,
                handle_size,
            )
            painter.drawRect(handle_rect)

    def get_rectangles(self):
        return [
            {
                "id": rect_id,
                "metadata": metadata,
                "coordinates": [rect.x(), rect.y(), rect.width(), rect.height()],
            }
            for rect, rect_id, metadata in self.rectangles
        ]

    def set_selected_rect_data(self, new_id, new_metadata):
        if self.selected_rect_index is not None:
            rect, _, _ = self.rectangles[self.selected_rect_index]
            self.rectangles[self.selected_rect_index] = (rect, new_id, new_metadata)
            self.rectangles_changed.emit()
            self.update()


class ImageEditorDialog(QDialog):
    def __init__(self, pil_image, rectangles=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rectangle Image Editor")
        self.showMaximized()

        self.image_label = ImageLabel()
        self.image_label.rectangles_changed.connect(self.update_rectangles_list)

        # Convert PIL image to QPixmap
        qimage = ImageQt(pil_image)
        pixmap = QPixmap.fromImage(qimage)
        self.image_label.setPixmap(pixmap)
        self.image_label.setScaledContents(True)  # Ensure content scales properly

        # Wrap the image label in a scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # Ensure scrolling adapts to the widget size
        scroll_area.setWidget(self.image_label)

        # Left-side layout for the image
        image_layout = QVBoxLayout()
        image_layout.addWidget(scroll_area)

        # Right-side layout for the rectangles list and controls
        controls_layout = QVBoxLayout()

        # List widget to display rectangles
        self.rectangles_list = QListWidget()
        self.rectangles_list.itemClicked.connect(self.select_rectangle_from_list)
        controls_layout.addWidget(self.rectangles_list)

        # Form for rectangle ID and metadata input
        form_layout = QFormLayout()
        self.id_input = QLineEdit()
        self.metadata_input = QLineEdit()
        form_layout.addRow("Rectangle ID:", self.id_input)
        form_layout.addRow("Metadata:", self.metadata_input)
        controls_layout.addLayout(form_layout)

        # Buttons for setting data and removing selected rectangle
        self.set_data_button = QPushButton("Set ID and Metadata")
        self.set_data_button.clicked.connect(self.set_rectangle_data)
        self.remove_button = QPushButton("Remove Rectangle")
        self.remove_button.clicked.connect(self.remove_selected_rectangle)

        controls_layout.addWidget(self.set_data_button)
        controls_layout.addWidget(self.remove_button)

        # Add OK and Cancel buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        controls_layout.addWidget(button_box)

        # Combine left and right layouts
        main_layout = QHBoxLayout()
        main_layout.addLayout(image_layout, 2)  # Image takes more space
        main_layout.addLayout(controls_layout, 1)

        self.setLayout(main_layout)

        # If rectangles are provided, set them
        if rectangles is not None:
            self.image_label.set_rectangles_from_data(rectangles)
            self.update_rectangles_list()

    def update_rectangles_list(self):
        """Update the list widget with the current rectangles."""
        self.rectangles_list.clear()
        for idx, (rect, rect_id, metadata) in enumerate(self.image_label.rectangles):
            item = QListWidgetItem(
                f"Rect {idx + 1}: ID={rect_id}, Metadata={metadata}, "
                f"Coords=({rect.x()}, {rect.y()}, {rect.width()}, {rect.height()})"
            )
            self.rectangles_list.addItem(item)
        # If a rectangle is selected in the image, select it in the list
        if self.image_label.selected_rect_index is not None:
            self.rectangles_list.setCurrentRow(self.image_label.selected_rect_index)
            rect, rect_id, metadata = self.image_label.rectangles[self.image_label.selected_rect_index]
            self.id_input.setText(rect_id)
            self.metadata_input.setText(metadata)
        else:
            self.id_input.clear()
            self.metadata_input.clear()

    def select_rectangle_from_list(self, item):
        """Select a rectangle from the list."""
        index = self.rectangles_list.row(item)
        self.image_label.selected_rect_index = index
        rect, rect_id, metadata = self.image_label.rectangles[index]
        self.id_input.setText(rect_id)
        self.metadata_input.setText(metadata)
        self.image_label.update()

    def set_rectangle_data(self):
        """Set the ID and metadata for the selected rectangle."""
        new_id = self.id_input.text()
        new_metadata = self.metadata_input.text()
        if new_id:
            self.image_label.set_selected_rect_data(new_id, new_metadata)
            self.update_rectangles_list()

    def remove_selected_rectangle(self):
        """Remove the selected rectangle."""
        if self.image_label.selected_rect_index is not None:
            self.image_label.rectangles.pop(self.image_label.selected_rect_index)
            self.image_label.selected_rect_index = None
            self.update_rectangles_list()
            self.image_label.update()

    def get_configurations(self):
        return self.image_label.get_rectangles()


# Main view to invoke the dialog
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load a sample PIL image
    pil_image = Image.new("RGB", (800, 600), "white")  # Example: a blank white image

    # Create some sample rectangles in the format you described
    sample_rectangles = [
        {"id": "Rect1", "metadata": "Metadata1", "coordinates": [100, 100, 200, 150]},
        {"id": "Rect2", "metadata": "Metadata2", "coordinates": [300, 250, 100, 100]},
    ]

    dialog = ImageEditorDialog(pil_image, rectangles=sample_rectangles)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        configurations = dialog.get_configurations()
        print("Rectangle configurations:")
        for config in configurations:
            print(config)

    sys.exit(app.exec())
