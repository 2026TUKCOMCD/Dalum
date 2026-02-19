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

        # 🔥 전신 fallback용 FaceDetection 추가
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
        expand_ratio: float = 1.08,
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

            points = np.array(points, dtype=np.int32)

            center = points.mean(axis=0)
            points = (points - center) * expand_ratio + center
            points = points.astype(np.int32)

            cv2.fillPoly(mask, [points], 255)

            face_center_y = int(center[1])
            mask[:face_center_y, :] = 255

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
            radius = int(max(bw, bh) * 0.7)

            cv2.circle(mask, (cx, cy), radius, 255, -1)

            # 얼굴 중심 기준 위 전부 제거
            mask[:cy, :] = 255

            mask = cv2.GaussianBlur(mask, (feather, feather), 0)

        return mask
    def get_face_and_below_mask(self, image):
        head_mask = self.get_head_mask(image)

        # head 아래 영역도 포함하는 마스크 생성
        h, w = head_mask.shape
        mask = np.zeros_like(head_mask)

        ys = np.where(head_mask > 0)[0]
        if len(ys) == 0:
            return mask

        bottom = ys.max()
        mask[bottom:, :] = 255

        return mask
