#얼굴 탐지용
import cv2
import mediapipe as mp


class FaceDetector:
    def __init__(self):
        self.detector = mp.solutions.face_detection.FaceDetection(
            model_selection=1,
            min_detection_confidence=0.5
        )

    def detect(self, image):
        """
        image: BGR np.ndarray
        return: [(x1, y1, x2, y2), ...]
        """
        h, w, _ = image.shape
        results = self.detector.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )

        boxes = []
        if results.detections:
            for det in results.detections:
                bbox = det.location_data.relative_bounding_box
                x1 = int(bbox.xmin * w)
                y1 = int(bbox.ymin * h)
                x2 = int((bbox.xmin + bbox.width) * w)
                y2 = int((bbox.ymin + bbox.height) * h)
                boxes.append((x1, y1, x2, y2))

        return boxes
