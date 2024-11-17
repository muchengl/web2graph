from typing import io

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QTextBrowser, QMessageBox
)
from PyQt6.QtCore import Qt

from fsm import WebGraph
from ui.image_dialog import ImageDialog


class MergeStateProjectDialog(QDialog):
    def __init__(self, fsm_graph: WebGraph):
        super().__init__()
        self.fsm_graph = fsm_graph

        # Initialize the UI
        self.init_ui()

        self.flag = False

    def init_ui(self):
        self.setWindowTitle("Merge State Project Dialog")
        self.setMinimumSize(400, 300)

        layout = QVBoxLayout()

        # Label to show current state information
        self.current_state_id = QLabel(f"Current State ID: {self.fsm_graph.current_state.id}")
        self.current_state_id.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.current_state_info = QLabel(f"Current State Information: {self.fsm_graph.current_state.state_info}")
        self.current_state_info.setAlignment(Qt.AlignmentFlag.AlignLeft)


        layout.addWidget(self.current_state_info)
        layout.addWidget(self.current_state_id)



        # ListWidget to select states to merge
        self.state_list = QListWidget()

        all_states = []
        for state in self.fsm_graph.states:
            all_states.append(state)

        self.state_list.addItems(all_states)

        self.state_list.itemClicked.connect(self.display_selected_state_info)
        layout.addWidget(self.state_list)

        # TextBrowser to display information about the selected state
        self.selected_state_info = QTextBrowser()
        self.selected_state_info.setPlaceholderText("Details of the selected state will be displayed here...")
        layout.addWidget(self.selected_state_info)

        # Button to open the current state's image
        self.open_image_button = QPushButton("Open Target State Image")
        self.open_image_button.clicked.connect(self.open_current_state_image)
        layout.addWidget(self.open_image_button)

        # Submit button
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_merge)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def display_selected_state_info(self, item):
        """Display information about the selected state."""
        state_name = item.text()
        self.state_id = state_name
        state = self.fsm_graph.states[state_name]

        # state_info = self.fsm_graph.get_state_info(state_name)  # Assuming fsm_graph has this method
        self.selected_state_info.setText(f"State: {state_name}\nName:{state.state_name} \nDetails:\n{state.state_info}")

    def open_current_state_image(self):
        """Open the image of the current state."""
        try:
            image = self.fsm_graph.states[self.state_id].som_image

            image.save("cache.png")

            image_path = "cache.png"

            d = ImageDialog(image_path)
            d.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while opening the image:\n{e}")

    def submit_merge(self):
        """Handle the submission process."""
        selected_items = self.state_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a state to merge.")
            return

        selected_state_id = selected_items[0].text()

        selected_state = self.fsm_graph.states[selected_state_id]
        self.fsm_graph.current_state.merge_into = selected_state

        self.fsm_graph.v_graph.add_node_pair(
            self.fsm_graph.current_state.id,
            selected_state.id,
            self.fsm_graph.current_state.state_info,
            selected_state.state_info,
            "green", "green"
        )

        QMessageBox.information(self, "Success", f"State {selected_state} has been successfully merged.")

        self.flag = True



