#이미지 URL → image 로드 유틸
import requests
import numpy as np
import cv2
from io import BytesIO

def load_image_from_url(url):
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    image_bytes = np.frombuffer(resp.content, np.uint8)
    image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError("Failed to decode image from URL")

    return image