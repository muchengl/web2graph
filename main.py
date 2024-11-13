from PIL.Image import Image
from PIL.ImageQt import ImageQt, QImage
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QToolBar, QFormLayout, QSplitter, QFileDialog, QDialog, QListWidget, QScrollArea,
    QMessageBox, QFrame
)
from PyQt6.QtGui import QPixmap, QAction
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import sys

from loguru import logger

from browser.actions import ClickAction, ActionType, TypeAction, Action, execute_action
from browser.browser_env import PlaywrightBrowserEnv, ScreenshotThread, BrowserStartThread, NavigateThread
from project.manager import new_project, ProjectManager
from project.metadata import ProjectMetadata
from ui.action_input_dialog import ActionInputBox
from ui.image_dialog import ImageDialog
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

        self.project_manager: ProjectManager=None


        self.current_web_image = None
        self.current_web_som: WebSOM = None
        self.image_som_enable = True




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

        self.switch_image_button = QPushButton("Switch Image")
        self.switch_image_button.clicked.connect(self.switch_image)

        # Left widget container
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.image_scroll_area)
        left_layout.addWidget(self.switch_image_button)
        left_widget.setLayout(left_layout)




        # ====================== Right ===========================
        # Right side: Input fields with a save button and URL input
        right_widget = QWidget()
        input_layout = QVBoxLayout()


        # project information
        self.label_title = QLabel(f"Please open or create a project.")
        # self.label_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label_title.setWordWrap(True)
        input_layout.addWidget(self.label_title)

        self.add_horizontal_line(input_layout)


        # action list
        self.action_list_title = QLabel(f"Action List:")

        self.som_list = QListWidget()
        self.som_list.setFixedHeight(200)

        input_layout.addWidget(self.action_list_title)
        input_layout.addWidget(self.som_list)
        self.som_list.itemDoubleClicked.connect(self.action_list_double_clicked)

        self.add_horizontal_line(input_layout)

        # ====================== hide ===========================
        self.current_state_info = QLabel(f"Current State Info:")
        input_layout.addWidget(self.current_state_info)

        # Add state input form elements to the right-side layout
        self.action_name_input = QLineEdit()
        self.action_info_input = QLineEdit()

        self.state_name_input = QLineEdit()
        self.state_info_input = QLineEdit()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_state)

        # State form layout to collect state name and info
        self.state_form_layout = QFormLayout()
        self.state_form_layout.addRow("Action Name:", self.action_name_input)
        self.state_form_layout.addRow("Action Info:", self.action_info_input)
        self.state_form_layout.addRow("State Name:", self.state_name_input)
        self.state_form_layout.addRow("State Info:", self.state_info_input)
        input_layout.addLayout(self.state_form_layout)
        input_layout.addWidget(self.save_button)

        self.add_horizontal_line(input_layout)

        # Current Webpage
        self.capture_button = QPushButton("Current Webpage")
        self.capture_button.clicked.connect(self.capture_current_web_page)
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
        self.toolbar = QToolBar("Project Management")
        self.addToolBar(self.toolbar)

        # Add action for new project
        new_action = QAction("New Project", self)
        new_action.triggered.connect(self.new_project_dialog)
        self.toolbar.addAction(new_action)

        open_action = QAction("Open Project", self)
        open_action.triggered.connect(self.open_project_dialog)
        self.toolbar.addAction(open_action)


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
            som=self.current_web_som
        )
        self.project_manager.save_project()

        self.label_title.setText(f"Name: {self.project_manager.metadata.name} \n"
                                 f"Path: {self.project_manager.metadata.path} \n"
                                 f"URL: {self.project_manager.metadata.url} \n")

        self._show_state_info(
            '',
            '',
            self.project_manager.fsm_graph.current_state.state_name,
            self.project_manager.fsm_graph.current_state.state_info
        )


    def open_project_dialog(self):

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

        # init image
        som = WebSOM(
            self.project_manager.fsm_graph.current_state.som_image,
            self.project_manager.fsm_graph.current_state.label_coordinates,
            self.project_manager.fsm_graph.current_state.parsed_content
        )
        self.handle_som(som)
        self.current_web_image = self.project_manager.fsm_graph.current_state.web_image


        # move to root state
        self.browser.navigate_to_sync(self.project_manager.url)

        self.label_title.setText(f"Name: {self.project_manager.metadata.name} \n"
                                 f"Path: {self.project_manager.metadata.path} \n"
                                 f"URL: {self.project_manager.metadata.url} \n")
        self.add_graph_bar()

        self._show_state_info(
            '',
            '',
            self.project_manager.fsm_graph.current_state.state_name,
            self.project_manager.fsm_graph.current_state.state_info
        )


    def capture_current_web_page(self):
        image = self.browser.take_full_screenshot_sync()
        image.save("current_web_page.png")
        d = ImageDialog("current_web_page.png")
        d.exec()


    """
    Utils
    
    """

    def action_list_double_clicked(self, item):
        list_idx = self.som_list.row(item)

        logger.info(f"You double-clicked item {list_idx + 1}: {item.text()}")

        box = ActionInputBox(f"{list_idx + 1}: {item.text()}")

        if box.exec() != QDialog.DialogCode.Accepted:
            return

        selected_action, action_content, action_name, action_info = box.get_data()
        logger.info(f"Action: {selected_action} , Action_content: {action_content}, Info: {action_info}")

        # execute action
        self.executed_action = execute_action(
            list_idx=list_idx,
            current_web_image=self.current_web_image,
            current_web_som=self.current_web_som,
            browser=self.browser,
            selected_action=selected_action,
            action_info=action_info,
            action_content=action_content
        )
        self._process_current_state()
        self.display_screenshot(self.current_web_som.processed_image)



        self._show_state_info(
            action_name,
            action_info,
            self.project_manager.fsm_graph.current_state.state_name,
            self.project_manager.fsm_graph.current_state.state_info
        )

        # # save FSM Graph
        # self.project_manager.fsm_graph.insert_and_move(
        #     action_name=action_name,
        #     action_info=action_info,
        #     action=executed_action,
        #     state_name='',
        #     state_info='',
        #     web_image=self.current_web_image,
        #     som=self.current_web_som
        # )
        # self.project_manager.save_project()


        #
        # self.state_form_layout.labelForField(self.action_name_input).setVisible(True)
        # self.state_form_layout.labelForField(self.action_info_input).setVisible(True)
        # self.state_form_layout.labelForField(self.state_name_input).setVisible(True)
        # self.state_form_layout.labelForField(self.state_info_input).setVisible(True)
        #
        # self.action_name_input.setVisible(True)
        # self.action_info_input.setVisible(True)
        # self.state_name_input.setVisible(True)
        # self.state_info_input.setVisible(True)
        #
        # self.save_button.setVisible(True)



    def save_state(self):
        action_name = self.action_name_input.text()
        action_info = self.action_info_input.text()

        state_name = self.state_name_input.text()
        state_info = self.state_info_input.text()

        # Execute the save FSM Graph code with the inputted state name and info
        self.project_manager.fsm_graph.insert_node(
            action_name=action_name,
            action_info=action_info,
            action=self.executed_action,
            state_name=state_name,
            state_info=state_info,
            web_image=self.current_web_image,
            som=self.current_web_som
        )
        self.project_manager.save_project()

        # Hide the state form after saving
        # self.state_form_layout.labelForField(self.action_name_input).setVisible(False)
        # self.state_form_layout.labelForField(self.action_info_input).setVisible(False)
        # self.state_form_layout.labelForField(self.state_name_input).setVisible(False)
        # self.state_form_layout.labelForField(self.state_info_input).setVisible(False)
        #
        # self.action_name_input.setVisible(False)
        # self.action_info_input.setVisible(False)
        # self.state_name_input.setVisible(False)
        # self.state_info_input.setVisible(False)
        #
        # self.save_button.setVisible(False)

        # Clear the form inputs for next use
        # self.state_name_input.clear()
        # self.state_info_input.clear()


    def _show_state_info(self,
                         action_name='',
                         action_info='',
                         state_name='',
                         state_info=''):
        self.action_name_input.setText(action_name)
        self.action_info_input.setText(action_info)
        self.state_name_input.setText(state_name)
        self.state_name_input.setText(state_info)


    def _process_current_state(self):
        self.current_web_image = self.browser.take_full_screenshot_sync()

        current_web_som = process_image_with_models(
            image=self.current_web_image,
            som_model=self.model_manager.get_som_model(),
            caption_model_processor=self.model_manager.get_caption_model()
        )

        self.handle_som(current_web_som)


    def handle_som(self, web_som: WebSOM):

        self.current_web_som = web_som

        processed_image = web_som.processed_image
        parsed_content_list = web_som.parsed_content
        label_coordinates = web_som.label_coordinates

        qt_image = ImageQt(processed_image)
        pixmap = QPixmap.fromImage(qt_image)

        self.pixmap = pixmap
        self.resize_image()

        self.som_list.clear()
        for parsed_content in parsed_content_list:
            print(parsed_content)
            self.som_list.addItem(parsed_content)

        logger.info(label_coordinates)


    def display_screenshot(self, pil_image):
        if pil_image==self.current_web_image:
            self.image_som_enable = False
        else:
            self.image_som_enable = True

        self.pixmap = pil_image_to_qpixmap(pil_image)
        self.resize_image()


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


    def switch_image(self):
        if self.image_som_enable:
            self.display_screenshot(self.current_web_image)
        else:
            self.display_screenshot(self.current_web_som.processed_image)


    def add_graph_bar(self):
        fsm_action = QAction("Show FSM Graph", self)
        fsm_action.triggered.connect(self.project_manager.fsm_graph.show)
        self.toolbar.addAction(fsm_action)

    def add_horizontal_line(self, layout):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())