import cv2
import numpy as np


class GarmentSegmentor:

    def segment(self, rgba: np.ndarray) -> np.ndarray:

        alpha = rgba[:, :, 3]

        # rembg가 만든 foreground 기준
        fg = alpha > 0

        # 상단 영역 제거 (얼굴/머리 컷)
        h, w = fg.shape
        top_cut = int(h * 0.18)   
        fg[:top_cut, :] = False

        # 너무 작은 컴포넌트 제거 (머리카락 찌꺼기)
        fg = self._remove_small_components(fg, min_area=2000)

        # 옷 형태 smooth
        kernel = np.ones((7, 7), np.uint8)
        fg = cv2.morphologyEx(fg.astype(np.uint8), cv2.MORPH_CLOSE, kernel)
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, kernel)

        return fg.astype(bool)

    def _remove_small_components(self, mask, min_area):
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
            mask.astype(np.uint8), connectivity=8
        )

        cleaned = np.zeros_like(mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] >= min_area:
                cleaned[labels == i] = 1

        return cleaned