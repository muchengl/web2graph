import asyncio
from importlib.metadata import metadata

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
from project.manager import new_project, ProjectManager
from project.metadata import ProjectMetadata
from ui.action_input_dialog import ActionInputBox
from ui.new_project_input_dialog import NewProjectInputDialog
from ui.open_project_input_dialog import OpenProjectInputDialog
from utils.image_util import pil_image_to_qpixmap
from web_parser.model_manager import ModelManager
from web_parser.omni_parser import WebParserThread, WebSOM, initialize_models, process_image_with_models


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.model_manager = ModelManager(
            som_model_path='models/icon_detect/best.pt',
            caption_model_name="blip2",
            caption_model_path="models/icon_caption_blip2"
        )

        browser = PlaywrightBrowserEnv()
        self.browser = browser
        self.browser.start_browser_sync()

        self.project_manager=None



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


        # som = QVBoxLayout()
        self.som_list = QListWidget()
        self.som_list.setFixedHeight(200)
        input_layout.addWidget(self.som_list)
        self.som_list.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.capture_button = QPushButton("Generate SOM")
        self.capture_button.clicked.connect(self.gen_som)
        input_layout.addWidget(self.capture_button)

        right_widget.setLayout(input_layout)




        #  ====================== Layout ===========================
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
        new_action.triggered.connect(self.new_project_dialog)
        toolbar.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project_dialog)
        toolbar.addAction(open_action)


    """
    Capture Screenshot
    """

    def capture_screenshot(self):
        url = self.url_input.text()
        if url:

            self.browser.start_browser_sync()
            self.browser.navigate_to_sync(url)

            self.current_web_image = self.browser.take_full_screenshot_sync()
            self.display_screenshot(self.current_web_image)


    def display_screenshot(self, pil_image):
        self.pixmap = pil_image_to_qpixmap(pil_image)
        self.resize_image()


    """
    Generate SOM
    """

    def gen_som(self):
        self.screenshot_thread = WebParserThread(
            self.current_web_image,
            som_model=self.model_manager.get_som_model(),
            caption_model_processor=self.model_manager.get_caption_model()
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


    def _process_current_state(self):
        self.current_web_image = self.browser.take_full_screenshot_sync()

        self.som = process_image_with_models(
            image=self.current_web_image,
            som_model=self.model_manager.get_som_model(),
            caption_model_processor=self.model_manager.get_caption_model()
        )

        self.handle_som(self.som)


    def new_project_dialog(self):

        dialog = NewProjectInputDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        project_path = dialog.path_input.text()
        project_name = dialog.name_input.text()
        project_url = dialog.url_input.text()

        project_path = project_path+'/'+project_name

        logger.info(f"New Project Created:\n "
                    f"Path: {project_path} \n"
                    f"Name: {project_name} \n"
                    f"URL: {project_url}")

        self.browser.navigate_to_sync(project_url)

        self._process_current_state()

        metadata = ProjectMetadata(
            project_path,
            project_name,
            project_url
        )

        self.project_manager = new_project(
            browse_env=self.browser,
            metadata=metadata,
            web_image=self.current_web_image,
            som_image=self.som.processed_image,
            ocr_result=self.current_web_som.ocr_result,
            parsed_content=self.current_web_som.parsed_content
        )
        self.project_manager.save_project()


    def open_project_dialog(self):

        dialog = OpenProjectInputDialog()
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        project_path = dialog.path_input.text()


        logger.info(f"New Project Created:\n "
                    f"Path: {project_path} \n")


        metadata = ProjectMetadata(project_path)

        self.project_manager = ProjectManager(metadata, self.browser)

        self.project_manager.load_project()

        som = WebSOM(
            self.project_manager.fsm_graph.current_state.som_image,
            self.project_manager.fsm_graph.current_state.ocr_result,
            self.project_manager.fsm_graph.current_state.parsed_content
        )
        self.handle_som(som)



    """
    Utils
    
    """

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



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())