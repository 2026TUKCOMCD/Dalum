import cv2
import numpy as np
import mediapipe as mp


class FaceContourMasker:

    def __init__(self):
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )

        # MediaPipe Face Oval Landmark
        self.FACE_OVAL = [
            10, 338, 297, 332, 284, 251, 389, 356,
            454, 323, 361, 288, 397, 365, 379,
            378, 400, 377, 152, 148, 176, 149,
            150, 136, 172, 58, 132, 93, 234,
            127, 162, 21, 54, 103, 67, 109
        ]

    # 얼굴 + 머리 + 얼굴 위 전부 제거
    def get_head_mask(
        self,
        image: np.ndarray,
        expand_ratio: float = 1.1,
        feather: int = 25
    ) -> np.ndarray:
        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        if feather % 2 == 0:
            feather += 1

        results = self.face_mesh.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )

        if not results.multi_face_landmarks:
            return mask

        landmarks = results.multi_face_landmarks[0]

        points = []
        for idx in self.FACE_OVAL:
            lm = landmarks.landmark[idx]
            points.append([int(lm.x * w), int(lm.y * h)])

        points = np.array(points, dtype=np.int32)

        # 얼굴 영역 확장
        center = points.mean(axis=0)
        points = (points - center) * expand_ratio + center
        points = points.astype(np.int32)

        # 얼굴 윤곽
        cv2.fillPoly(mask, [points], 255)

        # 얼굴 위 (머리 영역) 전부 제거
        face_top = np.min(points[:, 1])
        mask[:face_top, :] = 255

        # 경계 부드럽게
        mask = cv2.GaussianBlur(mask, (feather, feather), 0)

        return mask

    # 얼굴만 제거 (모자/머리카락 보존)
    def get_face_and_below_mask(
        self,
        image: np.ndarray,
        expand_ratio: float = 1.05,
        feather: int = 25
    ) -> np.ndarray:
        
        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        if feather % 2 == 0:
            feather += 1

        results = self.face_mesh.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )

        if not results.multi_face_landmarks:
            return mask

        landmarks = results.multi_face_landmarks[0]

        points = []
        for idx in self.FACE_OVAL:
            lm = landmarks.landmark[idx]
            points.append([int(lm.x * w), int(lm.y * h)])

        points = np.array(points, dtype=np.int32)

        # 얼굴 영역 살짝 확장
        center = points.mean(axis=0)
        points = (points - center) * expand_ratio + center
        points = points.astype(np.int32)

        # 얼굴 영역
        cv2.fillPoly(mask, [points], 255)

        # 얼굴 최하단 기준
        face_bottom = np.max(points[:, 1])

        # 얼굴 아래 전부 제거
        mask[face_bottom:, :] = 255

        mask = cv2.GaussianBlur(mask, (feather, feather), 0)

        return mask

