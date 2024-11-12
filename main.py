import asyncio

from PIL.Image import Image
from PIL.ImageQt import ImageQt, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QToolBar, QFormLayout, QSplitter, QFileDialog, QDialog, QListWidget, QScrollArea,
    QMessageBox
)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys

from loguru import logger
from playwright.sync_api import sync_playwright

from browser.actions import ClickAction, ActionType, TypeAction
from browser.browser_env import PlaywrightBrowserEnv, ScreenshotThread, BrowserStartThread, NavigateThread
from ui.action_input_dialog import ActionInputBox
from web_parser.omni_parser import WebParserThread, WebSOM, initialize_models


class ProjectDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Project")
        self.setGeometry(200, 200, 400, 300)

        # Layout for the dialog
        layout = QVBoxLayout()

        # Project path selection
        self.path_label = QLabel("Project Path:")
        self.path_input = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse_path)

        # Layout for path selection
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(self.browse_button)

        # Add path selection to the main layout
        layout.addWidget(self.path_label)
        layout.addLayout(path_layout)

        # Form layout for additional project details
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.description_input = QLineEdit()
        self.author_input = QLineEdit()
        self.date_input = QLineEdit()

        form_layout.addRow("Project Name:", self.name_input)
        form_layout.addRow("Project Name:", self.name_input)

        # form_layout.addRow("Description:", self.description_input)
        # form_layout.addRow("Author:", self.author_input)
        # form_layout.addRow("Date:", self.date_input)

        layout.addLayout(form_layout)

        # Save and cancel buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)  # Accept dialog
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)  # Reject dialog
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def browse_path(self):
        # Open file dialog to select directory path
        path = QFileDialog.getExistingDirectory(self, "Select Project Directory")
        if path:
            self.path_input.setText(path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.som_model, self.caption_model_processor = initialize_models(
            som_model_path='models/icon_detect/best.pt',
            caption_model_name="blip2",
            caption_model_path="models/icon_caption_blip2"
        )

        # Set the main window properties
        self.setWindowTitle("web2graph")
        self.showMaximized()  # Set the window to open in full-screen mode

        # Create the main widget and set the layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Create the project management toolbar
        self.create_toolbar()

        # Create a splitter for adjustable layout between image and input sections
        self.splitter = QSplitter(Qt.Orientation.Horizontal)



        # ====================== Left ===========================
        # Left side: Image display window with scroll area
        self.image_scroll_area = QScrollArea()
        self.image_scroll_area.setWidgetResizable(True)

        # Create QLabel for displaying the image inside the scroll area
        self.image_label = QLabel("Image Display")
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid black;")
        pixmap = QPixmap(300, 300)
        pixmap.fill(Qt.GlobalColor.lightGray)  # Placeholder color
        self.image_label.setPixmap(pixmap)

        # Set QLabel as the widget of QScrollArea
        self.image_scroll_area.setWidget(self.image_label)

        # Left widget container
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_scroll_area)
        left_widget.setLayout(left_layout)





        # ====================== Right ===========================
        # Right side: Input fields with a save button and URL input
        right_widget = QWidget()
        input_layout = QVBoxLayout()


        # URL input field
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL here")
        self.capture_button = QPushButton("Capture Screenshot")
        self.capture_button.clicked.connect(self.capture_screenshot)

        # Add URL input and button to layout
        # input_layout.addWidget(QLabel("URL:"))
        input_layout.addWidget(self.url_input)
        input_layout.addWidget(self.capture_button)

        # Add other form fields (e.g., Project Name, Description, Author, Date)
        # form_layout = QFormLayout()
        # self.name_input = QLineEdit()
        # self.description_input = QLineEdit()
        # self.author_input = QLineEdit()
        # self.date_input = QLineEdit()
        #
        # form_layout.addRow("Project Name:", self.name_input)
        # form_layout.addRow("Description:", self.description_input)
        # form_layout.addRow("Author:", self.author_input)
        # form_layout.addRow("Date:", self.date_input)
        #
        # # Add the form layout to the input layout
        # input_layout.addLayout(form_layout)

        # Save button at the bottom
        # self.save_button = QPushButton("Save")
        # self.save_button.clicked.connect(self.save_project)
        # input_layout.addWidget(self.save_button)

        # Set right side layout
        # right_widget.setLayout(input_layout)




        # som = QVBoxLayout()
        self.som_list = QListWidget()
        self.som_list.setFixedHeight(200)
        input_layout.addWidget(self.som_list)
        self.som_list.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.capture_button = QPushButton("Generate SOM")
        self.capture_button.clicked.connect(self.gen_som)
        input_layout.addWidget(self.capture_button)

        right_widget.setLayout(input_layout)





        # Add widgets to splitter
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(right_widget)

        # Set initial sizes of the left and right widgets
        self.splitter.setSizes([int(self.width() * 0.7), int(self.width() * 0.3)])  # Set initial size ratios

        # Set style for the splitter handle to make it visible
        self.splitter.setStyleSheet("QSplitter::handle { background-color: gray; }")
        self.splitter.setHandleWidth(2)

        # Connect splitter move event to resize image
        self.splitter.splitterMoved.connect(self.resize_image)

        # Add the splitter to the main layout
        main_layout.addWidget(self.splitter)


    def create_toolbar(self):
        toolbar = QToolBar("Project Management")
        self.addToolBar(toolbar)

        # Add action for new project
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.open_new_project_dialog)
        toolbar.addAction(new_action)

        open_action = QAction("Open Project", self)
        # new_action.triggered.connect(self.open_new_project_dialog)
        toolbar.addAction(open_action)


    """
    Capture Screenshot
    """

    def capture_screenshot(self):
        # Get URL from input field
        url = self.url_input.text()
        if url:
            browser = PlaywrightBrowserEnv()
            self.browser = browser

            browser.start_browser_sync()
            browser.navigate_to_sync(url)

            self.current_web_image = browser.take_full_screenshot_sync()
            self.display_screenshot(self.current_web_image)

            # print("screenshot")
            # self.screenshot_thread = ScreenshotThread(browser)
            # self.screenshot_thread.finished_signal.connect(self.display_screenshot)
            # self.screenshot_thread.start()

    def display_screenshot(self, pil_image):
        self.pixmap = self._pil_image_to_qpixmap(pil_image)
        self.resize_image()


    """
    Generate SOM
    """

    def gen_som(self):

        # self.screenshot_thread = WebParserThread(
        #     self.current_web_image,
        #     som_model_path='models/icon_detect/best.pt',
        #     caption_model_name="blip2",
        #     caption_model_path="models/icon_caption_blip2"
        # )

        self.screenshot_thread = WebParserThread(
            self.current_web_image,
            som_model=self.som_model,
            caption_model_processor=self.caption_model_processor
        )

        self.screenshot_thread.result_signal.connect(
            self.handle_som
        )
        self.screenshot_thread.start()

    def handle_som(self, web_som: WebSOM):

        self.current_web_som = web_som

        processed_image = web_som.processed_image
        parsed_content_list = web_som.parsed_content
        ocr_bbox_rslt = web_som.ocr_result

        qt_image = ImageQt(processed_image)
        pixmap = QPixmap.fromImage(qt_image)

        self.pixmap = pixmap
        self.resize_image()

        self.som_list.clear()
        for parsed_content in parsed_content_list:
            print(parsed_content)
            self.som_list.addItem(parsed_content)


        for i in range(len(ocr_bbox_rslt[0])):
            print(ocr_bbox_rslt[0][i], end=' -> ')
            print(ocr_bbox_rslt[1][i], end='\n\n')



        # action = ClickAction(
        #     self.current_web_image,
        #     web_som,
        #     action_content='2'
        # )
        #
        # action.execute(self.browser)
        # self.current_web_image = self.browser.take_full_screenshot_sync()
        # self.display_screenshot(self.current_web_image)

    def on_item_double_clicked(self, item):
        list_idx = self.som_list.row(item)
        # QMessageBox.information(self, "Item Double Clicked", f"You double-clicked item {list_idx + 1}: {item.text()}")
        logger.info(f"You double-clicked item {list_idx + 1}: {item.text()}")

        box = ActionInputBox(f"{list_idx + 1}: {item.text()}")
        if box.exec() == QDialog.DialogCode.Accepted:
            selected_action, input_text = box.get_data()
            logger.info(f"Action: {selected_action} , {input_text}")

            if ActionType[selected_action] == ActionType.CLICK:
                logger.info("taking CLICK...")
                action = ClickAction(
                    self.current_web_image,
                    self.current_web_som,
                    action_target_id=list_idx,
                    action_content=list_idx
                )

                action.execute(self.browser)
                self.current_web_image = self.browser.take_full_screenshot_sync()
                self.display_screenshot(self.current_web_image)

            elif ActionType[selected_action] == ActionType.TYPE:

                logger.info("taking TYPE...")
                action = TypeAction(
                    self.current_web_image,
                    self.current_web_som,
                    action_target_id=list_idx,
                    action_content=input_text
                )

                action.execute(self.browser)
                self.current_web_image = self.browser.take_full_screenshot_sync()
                self.display_screenshot(self.current_web_image)




    def resize_image(self):
        # Adjust the pixmap size to fit the label whenever the splitter is moved
        if hasattr(self, 'pixmap'):
            self.image_label.setPixmap(self.pixmap.scaled(
                self.image_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio
            ))



    def resizeEvent(self, event):
        # Ensure image resizes when window size changes
        self.resize_image()
        super().resizeEvent(event)


    def save_project(self):
        # Save button logic
        project_name = self.name_input.text()
        description = self.description_input.text()
        author = self.author_input.text()
        date = self.date_input.text()
        print("Project Saved!")
        print(f"Name: {project_name}")
        print(f"Description: {description}")
        print(f"Author: {author}")
        print(f"Date: {date}")

    def open_new_project_dialog(self):
        # Open the New Project dialog
        dialog = ProjectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            project_path = dialog.path_input.text()
            project_name = dialog.name_input.text()
            description = dialog.description_input.text()
            author = dialog.author_input.text()
            date = dialog.date_input.text()
            print("New Project Created!")
            print(f"Path: {project_path}")
            print(f"Name: {project_name}")
            print(f"Description: {description}")
            print(f"Author: {author}")
            print(f"Date: {date}")

    def _pil_image_to_qpixmap(self, pil_image):
        pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_ARGB32)

        # qt_image = ImageQt(pil_image)
        qpixmap = QPixmap.fromImage(qimage)
        return qpixmap



# Main application setup
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())