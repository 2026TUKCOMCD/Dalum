import cv2
import numpy as np
from rembg import remove


class SegmentationProcessor:
    """
    인물 / 단품 공통 segmentation 처리기
    - 배경 제거
    - RGBA 반환
    - contour 유지
    """

    def __init__(self):
        pass

    def remove_background(self, image: np.ndarray) -> np.ndarray:
        """
        배경 제거 후 RGBA 반환
        """
        _, buffer = cv2.imencode(".png", image)
        result = remove(buffer.tobytes())

        rgba = cv2.imdecode(
            np.frombuffer(result, np.uint8),
            cv2.IMREAD_UNCHANGED
        )

        return rgba

    def get_foreground_bbox(self, rgba: np.ndarray):
        """
        투명 제외 foreground bounding box 반환
        """
        alpha = rgba[:, :, 3]
        ys, xs = np.where(alpha > 10)

        if len(xs) == 0 or len(ys) == 0:
            return None

        x1, x2 = xs.min(), xs.max()
        y1, y2 = ys.min(), ys.max()

        return x1, y1, x2, y2

    def center_and_pad(self, rgba: np.ndarray, size=512):
        """
        중앙 정렬 + padding + resize
        """

        bbox = self.get_foreground_bbox(rgba)
        if bbox is None:
            return cv2.resize(rgba, (size, size))

        x1, y1, x2, y2 = bbox
        cropped = rgba[y1:y2, x1:x2]

        h, w = cropped.shape[:2]
        scale = size / max(h, w)

        resized = cv2.resize(
            cropped,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

        canvas = np.zeros((size, size, 4), dtype=np.uint8)

        y_offset = (size - resized.shape[0]) // 2
        x_offset = (size - resized.shape[1]) // 2

        canvas[
            y_offset:y_offset + resized.shape[0],
            x_offset:x_offset + resized.shape[1]
        ] = resized

        return canvas
