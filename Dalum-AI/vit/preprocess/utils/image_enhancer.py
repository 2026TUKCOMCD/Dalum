import cv2
import numpy as np


def enhance_for_material(image: np.ndarray) -> np.ndarray:
    """
    재질 판별 전용 텍스처 강화
    - 스무딩 제거
    - 고주파 강조
    - 미세 질감 살림
    """

    # High-frequency 강조 (Laplacian)
    lap = cv2.Laplacian(image, cv2.CV_64F)
    lap = cv2.convertScaleAbs(lap)

    enhanced = cv2.addWeighted(image, 1.0, lap, 0.4, 0)

    # 약한 Sharpen
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    enhanced = cv2.filter2D(enhanced, -1, kernel)

    return enhanced
