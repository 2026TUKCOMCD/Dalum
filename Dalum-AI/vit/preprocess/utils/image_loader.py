# vit/preprocess/utils/image_loader.py

import requests
import numpy as np
import cv2


def load_image_from_url(url: str):
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            print(f"[SKIP] image download failed ({resp.status_code}) | {url}")
            return None

        image_bytes = np.frombuffer(resp.content, np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print(f"[SKIP] image decode failed | {url}")
            return None

        return image

    except requests.exceptions.RequestException as e:
        print(f"[SKIP] request error | {url} | {e}")
        return None
