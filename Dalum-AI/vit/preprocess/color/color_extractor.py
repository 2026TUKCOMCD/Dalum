import numpy as np
import cv2


class ColorExtractor:
    def __init__(self, k=3):
        self.k = k

    def extract_dominant_colors(self, rgba: np.ndarray):
        # foreground mask
        alpha = rgba[:, :, 3]
        mask = alpha > 0

        bgr_pixels = rgba[:, :, :3][mask]

        if len(bgr_pixels) == 0:
            return []

        # 광택 소재 자동 감지: p95 밝기 - 중앙 밝기 > 80이면 하이라이트 제거
        gray_vals = (0.299 * bgr_pixels[:, 2].astype(np.float32)
                     + 0.587 * bgr_pixels[:, 1].astype(np.float32)
                     + 0.114 * bgr_pixels[:, 0].astype(np.float32))
        if float(np.percentile(gray_vals, 95)) - float(np.median(gray_vals)) > 80:
            bright_thr = float(np.percentile(gray_vals, 85))
            filtered = bgr_pixels[gray_vals <= bright_thr]
            if len(filtered) < 50:
                filtered = bgr_pixels
        else:
            filtered = bgr_pixels

        # BGR → LAB 변환 후 KMeans (지각적으로 균일한 색 공간)
        lab_pixels = cv2.cvtColor(
            filtered.reshape(-1, 1, 3),
            cv2.COLOR_BGR2LAB
        ).reshape(-1, 3).astype(np.float32)

        # 샘플링 (속도 개선)
        if len(lab_pixels) > 5000:
            idx = np.random.choice(len(lab_pixels), 5000, replace=False)
            lab_pixels = lab_pixels[idx]
            filtered_sampled = filtered[idx] if len(filtered) > 5000 else filtered
        else:
            filtered_sampled = filtered

        criteria = (
            cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
            100,
            0.2,
        )

        n_colors = min(self.k, max(1, len(lab_pixels) // 100))
        compactness, labels, centers_lab = cv2.kmeans(
            lab_pixels,
            n_colors,
            None,
            criteria,
            10,
            cv2.KMEANS_RANDOM_CENTERS,
        )

        labels = labels.flatten()

        results = []
        for i in range(n_colors):
            ratio = float(np.sum(labels == i) / len(labels))

            # LAB 중심 → BGR → RGB → HEX
            lab_center = centers_lab[i].reshape(1, 1, 3).astype(np.uint8)
            bgr_center = cv2.cvtColor(lab_center, cv2.COLOR_LAB2BGR)[0][0]
            rgb = bgr_center[::-1].astype(int)

            hex_color = "#{:02X}{:02X}{:02X}".format(rgb[0], rgb[1], rgb[2])
            results.append((hex_color, ratio))

        # 비율 높은 순 정렬
        results.sort(key=lambda x: x[1], reverse=True)

        return results
