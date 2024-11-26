import base64
import io

from PIL.ImageQt import QImage
from PyQt6.QtGui import QPixmap


def pil_image_to_qpixmap(pil_image):
    pil_image = pil_image.convert("RGBA")
    data = pil_image.tobytes("raw", "RGBA")
    qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_ARGB32)

    # qt_image = ImageQt(pil_image)
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap


def pil_image_to_base64(image, format="png"):
    buffered = io.BytesIO()
    image.save(buffered, format=format)
    img_byte = buffered.getvalue()
    base64_str = base64.b64encode(img_byte).decode("utf-8")
    return base64_str