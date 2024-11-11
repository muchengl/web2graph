import asyncio

from PyQt6.QtCore import QThread, pyqtSignal

from web_parser.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
import torch
from ultralytics import YOLO
from PIL import Image
import base64
import io
import matplotlib.pyplot as plt

def process_image_with_models(
        image_path: str,
        som_model_path: str,
        caption_model_name: str,
        caption_model_path: str,
        box_threshold: float = 0.03,
        device: str = 'mps'):

    # Load YOLO model for object detection
    som_model = get_yolo_model(model_path=som_model_path)
    som_model.to(device)
    print(f'Model loaded to {device}')

    # Load caption model processor
    caption_model_processor = get_caption_model_processor(
        model_name=caption_model_name,
        model_name_or_path=caption_model_path,
        device=device
    )

    # Set up bounding box and scaling configuration
    img = Image.open(image_path)
    image_rgb = img.convert('RGB')
    box_overlay_ratio = img.size[0] / 3200
    draw_bbox_config = {
        'text_scale': 0.8 * box_overlay_ratio,
        'text_thickness': max(int(2 * box_overlay_ratio), 1),
        'text_padding': max(int(3 * box_overlay_ratio), 1),
        'thickness': max(int(3 * box_overlay_ratio), 1),
    }

    # Run OCR and bounding box filtering
    ocr_bbox_rslt, is_goal_filtered = check_ocr_box(
        image_path=image_path,
        display_img=False,
        output_bb_format='xyxy',
        goal_filtering=None,
        easyocr_args={'paragraph': False, 'text_threshold': 0.9},
        use_paddleocr=True)

    text, ocr_bbox = ocr_bbox_rslt

    # Get labeled image and content list
    dino_labeled_img, label_coordinates, parsed_content_list = get_som_labeled_img(
        img_path=image_path,
        model=som_model,
        BOX_TRESHOLD=box_threshold,
        output_coord_in_ratio=False,
        ocr_bbox=ocr_bbox,
        draw_bbox_config=draw_bbox_config,
        caption_model_processor=caption_model_processor,
        ocr_text=text,
        use_local_semantics=True,
        iou_threshold=0.1,
        imgsz=640
    )

    # Decode labeled image from base64
    processed_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))

    return processed_image, ocr_bbox_rslt, parsed_content_list

class WebParserThread(QThread):
    started_signal = pyqtSignal()
    result_signal = pyqtSignal(object, object, object)  # Signal to emit processed_image, ocr_bbox_rslt, parsed_content_list


    def __init__(self,
                 image_path: str,
                 som_model_path: str,
                 caption_model_name: str,
                 caption_model_path: str):
        super().__init__()
        self.image_path = image_path
        self.som_model_path = som_model_path
        self.caption_model_name = caption_model_name
        self.caption_model_path = caption_model_path

    def run(self):
        # Process the image and get results
        processed_image, ocr_bbox_rslt, parsed_content_list = process_image_with_models(
            self.image_path,
            self.som_model_path,
            self.caption_model_name,
            self.caption_model_path
        )

        # Emit the results after processing
        self.result_signal.emit(processed_image, ocr_bbox_rslt, parsed_content_list)
        self.started_signal.emit()


if __name__ == '__main__':
    # Example usage
    image_path = 'screenshot.png'
    # image = Image.open(image_path)

    processed_image, ocr_bbox_rslt, parsed_content_list = process_image_with_models(
        image_path=image_path,
        som_model_path='models/icon_detect/best.pt',
        caption_model_name="blip2",
        caption_model_path="models/icon_caption_blip2"
    )

    # Display processed image
    plt.figure(figsize=(12, 12))
    plt.imshow(processed_image)
    plt.axis('off')
    plt.show()

    # Print OCR bounding box results and parsed content
    for parsed_content in parsed_content_list:
        print(parsed_content)

    for i in range(len(ocr_bbox_rslt[0])):
        print(ocr_bbox_rslt[0][i], end=' -> ')
        print(ocr_bbox_rslt[1][i], end='\n\n')
