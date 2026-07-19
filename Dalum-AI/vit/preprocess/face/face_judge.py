import cv2
import mediapipe as mp
import numpy as np


_face_mesh = mp.solutions.face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=False,
    min_detection_confidence=0.5
)

# FaceMesh 통과 시 인덱스 점수가 이 값 미만이면 마네킹으로 거부
_INDEX_REJECT_TH = -0.08
# FaceMesh 실패해도 인덱스 점수가 이 값 이상이면 사람으로 인정 (fallback)
_INDEX_FALLBACK_TH = 0.12


def is_valid_face_mesh_loose(crop: np.ndarray) -> bool:
    h, w = crop.shape[:2]
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

    # 80 → 50: 측면/부분 얼굴도 허용
    return valid_cnt >= 50


def has_real_face(
    image,
    face_detector,
    face_index,
    similarity_th=0.72,
    debug=False,
    apply_bbox_filter=True
):

    h, w, _ = image.shape
    boxes = face_detector.detect(image)

    if not boxes:
        return False, 0.0

    best_score = 0.0

    for (x1, y1, x2, y2) in boxes:
        bw = x2 - x1
        bh = y2 - y1

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

        idx_score = face_index.score(crop)
        mesh_ok = is_valid_face_mesh_loose(crop)

        if debug:
            print(f"[FACE] mesh={mesh_ok} | idx_score={idx_score:.3f}")

        if mesh_ok:
            if idx_score > _INDEX_REJECT_TH:
                return True, idx_score
            else:
                if debug:
                    print(f"[FACE] FaceMesh OK but idx_score={idx_score:.3f} → 마네킹 거부")
                continue

        # FaceMesh 실패 → 인덱스 fallback
        if idx_score > _INDEX_FALLBACK_TH:
            if debug:
                print(f"[FACE] FaceMesh 실패 but idx_score={idx_score:.3f} → fallback 통과")
            return True, idx_score

        best_score = max(best_score, idx_score)

    return False, best_score
