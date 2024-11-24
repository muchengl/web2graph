import sys
from PyQt6.QtCore import Qt, QRect, QPoint
from PyQt6.QtGui import QPixmap, QPainter, QPen
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QFileDialog, QPushButton, QHBoxLayout


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.rectangles = []  # 存储绘制的矩形框

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_point = event.position().toPoint()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.drawing:
            self.end_point = event.position().toPoint()
            self.rectangles.append(QRect(self.start_point, self.end_point))
            self.drawing = False
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.pixmap() is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(Qt.GlobalColor.red, 2)
        painter.setPen(pen)
        for rect in self.rectangles:
            painter.drawRect(rect)
        if self.drawing and self.start_point and self.end_point:
            painter.drawRect(QRect(self.start_point, self.end_point))

    def get_rectangles(self):
        return [(rect.topLeft(), rect.bottomRight()) for rect in self.rectangles]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("画框工具")
        self.image_label = ImageLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 主布局
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)

        # 按钮布局
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("加载图片")
        self.load_button.clicked.connect(self.open_image)
        self.get_rectangles_button = QPushButton("获取框坐标")
        self.get_rectangles_button.clicked.connect(self.get_rectangles)

        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.get_rectangles_button)

        layout.addLayout(button_layout)

        # 主窗口容器
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap)

    def get_rectangles(self):
        rectangles = self.image_label.get_rectangles()
        print("框的顶点坐标:")
        for rect in rectangles:
            print(f"起点: {rect[0]}, 终点: {rect[1]}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec())
