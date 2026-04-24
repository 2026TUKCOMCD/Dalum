import cv2
import mediapipe as mp


class PoseHumanDetector:
    """
    MediaPipe Pose 기반
    얼굴이 없어도 사람(모델)인지 판단하기 위한 detector
    """

    VISIBLE_THRESHOLD = 0.5
    MIN_VISIBLE_LANDMARKS = 8

    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5
        )
        self.LM = mp.solutions.pose.PoseLandmark

    def _is_visible(self, lm):
        return lm.visibility >= self.VISIBLE_THRESHOLD

    def detect(self, image, return_landmarks=False):
        results = self.pose.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        )

        if not results.pose_landmarks:
            if return_landmarks:
                return False, None
            return False

        lm = results.pose_landmarks.landmark

        visible = [
            l for l in lm if self._is_visible(l)
        ]

        if len(visible) < self.MIN_VISIBLE_LANDMARKS:
            if return_landmarks:
                return False, results.pose_landmarks
            return False

        # 상체
        upper_body = (
            (self._is_visible(lm[self.LM.LEFT_SHOULDER]) and self._is_visible(lm[self.LM.RIGHT_SHOULDER])) or
            (self._is_visible(lm[self.LM.LEFT_SHOULDER]) and self._is_visible(lm[self.LM.LEFT_ELBOW])) or
            (self._is_visible(lm[self.LM.RIGHT_SHOULDER]) and self._is_visible(lm[self.LM.RIGHT_ELBOW]))
        )

        # 하체
        lower_body = (
            (self._is_visible(lm[self.LM.LEFT_HIP]) and self._is_visible(lm[self.LM.RIGHT_HIP])) or
            (self._is_visible(lm[self.LM.LEFT_HIP]) and self._is_visible(lm[self.LM.LEFT_KNEE])) or
            (self._is_visible(lm[self.LM.RIGHT_HIP]) and self._is_visible(lm[self.LM.RIGHT_KNEE]))
        )

        is_human = upper_body or lower_body

        if return_landmarks:
            return is_human, results.pose_landmarks

        return is_human

