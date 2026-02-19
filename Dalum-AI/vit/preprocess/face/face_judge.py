import cv2
import mediapipe as mp
import numpy as np


_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5
)


def is_valid_face_mesh_loose(crop: np.ndarray) -> bool:
    h, w, _ = crop.shape
    if h < 40 or w < 40:
        return False

    rgb = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    result = _face_mesh.process(rgb)

    if not result.multi_face_landmarks:
        return False

    lm = result.multi_face_landmarks[0].landmark
    valid_cnt = sum(
        0.0 <= p.x <= 1.0 and 0.0 <= p.y <= 1.0
        for p in lm
    )

    return valid_cnt >= 80


def has_real_face(
    image,
    face_detector,
    face_index,
    similarity_th=0.72,
    debug=False,
    apply_bbox_filter=True
):
    """
    return:
      - (is_face_candidate: bool, confidence: float)
    """

    h, w, _ = image.shape
    boxes = face_detector.detect(image)

    if not boxes:
        return False, 0.0

    best_sim = 0.0

    for (x1, y1, x2, y2) in boxes:
        bw = x2 - x1
        bh = y2 - y1

        # bbox 필터
        if apply_bbox_filter:
            area_ratio = (bw * bh) / (w * h)
            if area_ratio > 0.45:
                continue

            aspect = bw / (bh + 1e-6)
            if aspect < 0.5 or aspect > 2.0:
                continue

        crop = image[y1:y2, x1:x2]
        if crop.size == 0:
            continue

        # FaceMesh = 얼굴 후보
        if not is_valid_face_mesh_loose(crop):
            continue

        # face_index는 confidence 참고용
        sims = face_index.match_all(crop)
        best_sim = max(sims) if sims else 0.0

        if debug:
            print(f"[FACE] mesh OK | confidence={best_sim:.3f}")

        # 얼굴 후보 확정
        return True, best_sim

    return False, best_sim
