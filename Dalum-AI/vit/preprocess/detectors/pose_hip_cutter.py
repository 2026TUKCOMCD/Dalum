import cv2
import mediapipe as mp
import numpy as np


class PoseHipCutter:
    """
    MediaPipe Pose 기반
    - 허리 기준
    - 의류 실루엣(알파) 윤곽을 따라 곡선 컷
    """

    def __init__(self):
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            min_detection_confidence=0.5
        )

    # 상의 → 하체 제거 (곡선 컷)
    def cut_below_hip_contour(self, image, rgba, margin_ratio=0.03):
        h, w, _ = image.shape

        results = self.pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return rgba

        lm = results.pose_landmarks.landmark
        left_hip = lm[mp.solutions.pose.PoseLandmark.LEFT_HIP]
        right_hip = lm[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

        hip_y = int((left_hip.y + right_hip.y) / 2 * h)
        hip_y = max(0, int(hip_y - h * margin_ratio))

        alpha = rgba[:, :, 3]
        mask = alpha > 0

        # 각 column에서 실루엣의 가장 아래 지점 찾기
        bottom_curve = []

        for x in range(w):
            ys = np.where(mask[:, x])[0]
            if len(ys) > 0:
                bottom_curve.append(ys.max())
            else:
                bottom_curve.append(None)

        # hip 아래만 자연스럽게 제거
        for x in range(w):
            bottom_y = bottom_curve[x]
            if bottom_y is None:
                continue

            if bottom_y > hip_y:
                rgba[hip_y:bottom_y, x, 3] = 0

        return rgba
    
    # 하의 → 상체 제거 (곡선 컷)
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

        for x in range(w):
            column = silhouette[:, x]

            above = column[:hip_y]
            indices = np.where(above)[0]

            if len(indices) == 0:
                continue

            cut_end = indices[-1]

            rgba[:cut_end + 1, x, 3] = 0

        return rgba
