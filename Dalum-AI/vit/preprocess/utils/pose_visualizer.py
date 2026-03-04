import cv2
import mediapipe as mp


def draw_pose_debug(image, pose_landmarks, is_human: bool):
    """
    관절 + skeleton + 판별 결과를 이미지에 그려줌
    """
    debug_img = image.copy()

    if not pose_landmarks:
        cv2.putText(
            debug_img,
            "NO POSE DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 0, 255),
            2
        )
        return debug_img

    mp_draw = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose

    mp_draw.draw_landmarks(
        debug_img,
        pose_landmarks,
        mp_pose.POSE_CONNECTIONS
    )

    label = "MODEL (POSE)" if is_human else "PRODUCT"
    color = (0, 165, 255) if is_human else (0, 255, 0)

    cv2.putText(
        debug_img,
        label,
        (30, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        color,
        3
    )

    return debug_img
