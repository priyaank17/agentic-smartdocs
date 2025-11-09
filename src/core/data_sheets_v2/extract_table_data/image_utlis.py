"""This file contains information about the image-related tasks such as
encoding images and cropping them based on a bounding box."""

import base64
from io import BytesIO
from PIL import Image
from src.utils.log import logger


def get_cropped_image(image_data, bounding_box):
    """Crop image to bounding box."""
    logger.info("INIT: Cropping image to bounding box.")
    # image = Image.open(image_path)
    image = Image.open(BytesIO(image_data))
    x_min, y_min = float(bounding_box["x_min"]), float(bounding_box["y_min"])
    x_max, y_max = float(bounding_box["x_max"]), float(bounding_box["y_max"])
    cropped_image = image.crop((x_min, y_min, x_max, y_max))
    logger.info("DONE: Image cropped to bounding box.")
    return cropped_image


def encode_image_2(image):
    """Encode image to base64 string."""
    buffer = BytesIO()
    image.save(buffer, format=image.format if image.format else "PNG")
    base64_encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return base64_encoded_image
