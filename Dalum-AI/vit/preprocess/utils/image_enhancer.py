import cv2
import numpy as np


def enhance_for_material(image: np.ndarray) -> np.ndarray:
    # 1. CLAHE: L채널만 적용해 색상 왜곡 없이 대비 향상
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l = clahe.apply(l)
    enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

    # 2. Laplacian: 그레이스케일 기반으로 컬러 번짐 방지
    gray = cv2.cvtColor(enhanced, cv2.COLOR_BGR2GRAY)
    lap = cv2.Laplacian(gray, cv2.CV_64F)
    lap_3ch = cv2.cvtColor(cv2.convertScaleAbs(lap), cv2.COLOR_GRAY2BGR)
    enhanced = cv2.addWeighted(enhanced, 1.0, lap_3ch, 0.3, 0)

    # 3. Sharpen
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    enhanced = cv2.filter2D(enhanced, -1, kernel)

    return enhanced
