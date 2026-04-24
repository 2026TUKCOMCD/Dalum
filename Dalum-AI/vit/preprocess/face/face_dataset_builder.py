import os
import cv2
import numpy as np


class FaceDatasetBuilder:
    """
    얼굴 / 비얼굴 데이터셋 자동 수집기
    """

    def __init__(
        self,
        base_dataset_dir: str,
        face_detector,
        person_segmentor,
        min_face_size: int = 40
    ):
        self.face_detector = face_detector
        self.person_segmentor = person_segmentor
        self.min_face_size = min_face_size

        self.face_dir = os.path.join(base_dataset_dir, "face")
        self.not_human_dir = os.path.join(base_dataset_dir, "not_human")
        self.review_dir = os.path.join(base_dataset_dir, "review")

        os.makedirs(self.face_dir, exist_ok=True)
        os.makedirs(self.not_human_dir, exist_ok=True)
        os.makedirs(self.review_dir, exist_ok=True)

    def process(self, image: np.ndarray, image_id: str):
        """
        image_id: output 이미지 번호 (ex: 00000004)
        """

        h, w, _ = image.shape
        boxes = self.face_detector.detect(image)

        for idx, (x1, y1, x2, y2) in enumerate(boxes):
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            crop = image[y1:y2, x1:x2]
            if crop.size == 0:
                continue

            if crop.shape[0] < self.min_face_size or crop.shape[1] < self.min_face_size:
                continue

            is_real = self.person_segmentor.is_real_face(crop)

            # 🔥 핵심: output 번호 기반 파일명
            filename = f"{image_id}_face_{idx}.webp"

            if is_real:
                save_path = os.path.join(self.face_dir, filename)
            else:
                save_path = os.path.join(self.review_dir, filename)

            cv2.imwrite(save_path, crop)
