import numpy as np
import cv2


class ColorExtractor:
    def __init__(self, k=3):
        self.k = k

    def extract_dominant_colors(self, rgba: np.ndarray):
        """
        RGBA (512x512) 입력
        alpha > 0 인 foreground만 사용
        OpenCV kmeans로 dominant HEX 색상 추출
        """

        # foreground mask
        alpha = rgba[:, :, 3]
        mask = alpha > 0

        pixels = rgba[:, :, :3][mask]

        if len(pixels) == 0:
            return []

        # BGR → RGB 변환
        pixels = cv2.cvtColor(
            pixels.reshape(-1, 1, 3),
            cv2.COLOR_BGR2RGB
        ).reshape(-1, 3)

        # float32 변환 (kmeans 필수)
        pixels = np.float32(pixels)

        # 샘플링 (속도 개선)
        if len(pixels) > 5000:
            idx = np.random.choice(len(pixels), 5000, replace=False)
            pixels = pixels[idx]

        # OpenCV KMeans 설정
        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            100,
            0.2,
        )

        compactness, labels, centers = cv2.kmeans(
            pixels,
            self.k,
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS,
        )

        labels = labels.flatten()

        results = []

        for i in range(self.k):
            ratio = np.sum(labels == i) / len(labels)
            rgb = centers[i].astype(int)

            hex_color = "#{:02X}{:02X}{:02X}".format(
                rgb[0], rgb[1], rgb[2]
            )

            results.append((hex_color, ratio))

        # 비율 높은 순 정렬
        results.sort(key=lambda x: x[1], reverse=True)

        return results
