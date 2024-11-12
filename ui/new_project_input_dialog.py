from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit, QFormLayout, QFileDialog


class NewProjectInputDialog(QDialog):
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
        self.url_input = QLineEdit()


        form_layout.addRow("Project Name:", self.name_input)
        form_layout.addRow("Website URL:", self.url_input)


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
