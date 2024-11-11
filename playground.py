from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
import sys

from web_parser.omni_parser import WebParserThread


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Example setup for QLabel to display an image
        self.label = QLabel(self)
        self.setCentralWidget(self.label)

        # Start the WebParserThread
        self.thread = WebParserThread(
            image_path='screenshot.png',
            som_model_path='models/icon_detect/best.pt',
            caption_model_name="blip2",
            caption_model_path="models/icon_caption_blip2"
        )

        # Connect the signals
        self.thread.result_signal.connect(self.handle_results)
        self.thread.started_signal.connect(lambda: print("Processing started"))

        # Start the thread
        self.thread.start()

    def handle_results(self, processed_image, ocr_bbox_rslt, parsed_content_list):
        # Display the processed image in the QLabel (convert to QPixmap if needed)
        processed_image.show()  # This will open the image window. Adjust as needed.

        # Print OCR bounding box results and parsed content
        for parsed_content in parsed_content_list:
            print(parsed_content)

        for i in range(len(ocr_bbox_rslt[0])):
            print(ocr_bbox_rslt[0][i], end=' -> ')
            print(ocr_bbox_rslt[1][i], end='\n\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
