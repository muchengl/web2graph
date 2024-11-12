from PIL.ImageQt import QImage
from PyQt6.QtGui import QPixmap


def pil_image_to_qpixmap(pil_image):
    pil_image = pil_image.convert("RGBA")
    data = pil_image.tobytes("raw", "RGBA")
    qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_ARGB32)

    # qt_image = ImageQt(pil_image)
    qpixmap = QPixmap.fromImage(qimage)
    return qpixmap