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

        self.face_detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.3
        )

        self.FACE_OVAL = [
            10, 338, 297, 332, 284, 251, 389, 356,
            454, 323, 361, 288, 397, 365, 379,
            378, 400, 377, 152, 148, 176, 149,
            150, 136, 172, 58, 132, 93, 234,
            127, 162, 21, 54, 103, 67, 109
        ]

    def get_head_mask(
        self,
        image: np.ndarray,
        expand_ratio: float = 1.20,   # 1.08 → 1.20: 머리카락 영역까지 커버
        feather: int = 15
    ) -> np.ndarray:

        h, w, _ = image.shape
        mask = np.zeros((h, w), dtype=np.uint8)

        if feather % 2 == 0:
            feather += 1

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # FaceMesh 시도
        results = self.face_mesh.process(rgb)

        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]

            points = []
            for idx in self.FACE_OVAL:
                lm = landmarks.landmark[idx]
                points.append([int(lm.x * w), int(lm.y * h)])

            points = np.array(points, dtype=np.float32)
            center = points.mean(axis=0)
            expanded = ((points - center) * expand_ratio + center).astype(np.int32)

            # 얼굴 윤곽 폴리곤 마스킹 (직선이 아닌 얼굴 형태로 제거)
            cv2.fillPoly(mask, [expanded], 255)

            # 머리 위쪽(머리카락) 제거: 얼굴 상단 위만 직선 처리
            top_y = max(0, int(expanded[:, 1].min()) - 5)
            mask[:top_y, :] = 255

            mask = cv2.GaussianBlur(mask, (feather, feather), 0)
            return mask

        # FaceMesh 실패 → FaceDetection fallback
        detection = self.face_detector.process(rgb)

        if detection.detections:
            det = detection.detections[0]
            bbox = det.location_data.relative_bounding_box

            x1 = int(bbox.xmin * w)
            y1 = int(bbox.ymin * h)
            bw = int(bbox.width * w)
            bh = int(bbox.height * h)
            cx = x1 + bw // 2
            cy = y1 + bh // 2

            # 얼굴 타원 마스킹
            cv2.ellipse(mask, (cx, cy), (int(bw * 0.65), int(bh * 0.65)), 0, 0, 360, 255, -1)

            # 머리 위쪽(머리카락) 제거
            hair_top = max(0, y1 - int(bh * 0.35))
            mask[:hair_top, :] = 255

            mask = cv2.GaussianBlur(mask, (feather, feather), 0)
            return mask

        # 얼굴 미탐지 최후 수단: 상단 15% 제거
        mask[:int(h * 0.15), :] = 255
        mask = cv2.GaussianBlur(mask, (feather, feather), 0)
        return mask

    def get_face_and_below_mask(self, image):
        head_mask = self.get_head_mask(image)

        h, w = head_mask.shape
        mask = np.zeros_like(head_mask)

        ys = np.where(head_mask > 0)[0]
        if len(ys) == 0:
            return mask

        bottom = ys.max()
        mask[bottom:, :] = 255

        return mask
