import asyncio
from PyQt6.QtCore import QThread, pyqtSignal
from loguru import logger

from web_parser.utils import get_som_labeled_img, check_ocr_box, get_caption_model_processor, get_yolo_model
import torch
from ultralytics import YOLO
from PIL import Image
import base64
import io
import matplotlib.pyplot as plt


class WebSOM:
    def __init__(self, processed_image: Image.Image, label_coordinates, parsed_content):
        self.processed_image = processed_image
        # self.ocr_result = ocr_result
        self.label_coordinates = label_coordinates
        logger.info(type(label_coordinates))

        self.label_coordinates = {key: value.tolist() for key, value in label_coordinates.items()}

        self.parsed_content = parsed_content


def initialize_models(som_model_path: str, caption_model_name: str, caption_model_path: str, device: str = 'mps'):
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
    return som_model, caption_model_processor


def process_image_with_models(
        image: Image.Image,
        som_model,
        caption_model_processor,
        box_threshold: float = 0.03) -> WebSOM:

    logger.info("")

    image_path = 'cache.png'
    image.save(image_path, format='PNG')

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

    # logger.info(f"label_coordinates: {label_coordinates}")
    # logger.info(f"parsed_content_list: {parsed_content_list}")

    # Decode labeled image from base64
    processed_image = Image.open(io.BytesIO(base64.b64decode(dino_labeled_img)))

    # return WebSOM(processed_image, ocr_bbox_rslt, parsed_content_list)

    return WebSOM(processed_image, label_coordinates, parsed_content_list)


class WebParserThread(QThread):
    started_signal = pyqtSignal()
    result_signal = pyqtSignal(object)  # Signal to emit processed_image, ocr_bbox_rslt, parsed_content_list

    def __init__(self, image: Image.Image, som_model, caption_model_processor):
        super().__init__()
        self.image = image
        self.som_model = som_model
        self.caption_model_processor = caption_model_processor

    def run(self):
        # Process the image and get results
        result = process_image_with_models(
            self.image,
            self.som_model,
            self.caption_model_processor
        )

        # Emit the results after processing
        self.result_signal.emit(result)
        self.started_signal.emit()


if __name__ == '__main__':
    # Example usage
    image_path = 'cache.png'
    image = Image.open(image_path)

    # Initialize models only once
    som_model, caption_model_processor = initialize_models(
        som_model_path='models/icon_detect/best.pt',
        caption_model_name="blip2",
        caption_model_path="models/icon_caption_blip2"
    )

    # Process image with preloaded models
    result = process_image_with_models(
        image=image,
        som_model=som_model,
        caption_model_processor=caption_model_processor
    )

    # Display processed image
    plt.figure(figsize=(12, 12))
    plt.imshow(result.processed_image)
    plt.axis('off')
    plt.show()

    # Print OCR bounding box results and parsed content
    for parsed_content in result.parsed_content:
        print(parsed_content)

    for i in range(len(result.label_coordinates[0])):
        print(result.label_coordinates[0][i], end=' -> ')
        print(result.label_coordinates[1][i], end='\n\n')
