import cv2
import mediapipe as mp
import numpy as np


class PoseHipCutter:
    """
    MediaPipe Pose 기반
    - 허리 기준
    - 의류 실루엣(알파) 윤곽을 따라 하의 제거
    """

    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5
        )

    #상의사진 경우 -> 하체 제거
    def cut_below_hip_contour(self, image, rgba, margin_ratio=0.03):
        h, w, _ = image.shape

        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return rgba  # 포즈 못 잡으면 그대로

        lm = results.pose_landmarks.landmark
        left_hip = lm[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        hip_y = int((left_hip.y + right_hip.y) / 2 * h)
        hip_y = max(0, int(hip_y - h * margin_ratio))

        # 의류 실루엣 (rembg 결과)
        silhouette = rgba[:, :, 3] > 0

        # hip 아래 + 실루엣 영역만 제거
        rgba[hip_y:, :, 3][silhouette[hip_y:, :]] = 0

        return rgba
    
    #하의사진일 경우 -> 상체 제거
    def cut_above_hip_contour(self, image, rgba, margin_ratio=0.03):
        h, w, _ = image.shape

        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return rgba

        lm = results.pose_landmarks.landmark
        left_hip = lm[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        hip_y = int((left_hip.y + right_hip.y) / 2 * h)
        hip_y = min(h, int(hip_y + h * margin_ratio))

        silhouette = rgba[:, :, 3] > 0

        # hip 위 제거
        rgba[:hip_y, :, 3][silhouette[:hip_y, :]] = 0

        return rgba