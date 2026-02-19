import numpy as np
from rembg import remove
import cv2
from vit.preprocess.face.face_contour_masker import FaceContourMasker
from vit.preprocess.detectors.pose_hip_cutter import PoseHipCutter
from vit.preprocess.utils.category_cut_policy import (
    CATEGORY_CUT_POLICY,
    CutType,
    CutPolicy,
)


class ModelProcessor:
    def __init__(self):
        self.face_masker = FaceContourMasker()
        self.hip_cutter = PoseHipCutter()

    # TOP 전용 곡선 dynamic 컷
    def process_top_dynamic(self, image, rgba, ratio: float):

        h, w = rgba.shape[:2]
        alpha = rgba[:, :, 3]
        mask = alpha > 0

        ys = np.where(mask)[0]
        if len(ys) == 0:
            return rgba

        top_y = ys.min()
        bottom_y = ys.max()
        body_height = bottom_y - top_y
        body_ratio = body_height / h

        # 크롭 보정
        if body_ratio < 0.55:
            ratio = min(ratio, 0.55)

        # 앉은 포즈 → pose 컷으로 전환
        if body_ratio > 0.72:
            return self.hip_cutter.cut_below_hip_contour(
                image, rgba, margin_ratio=0.02
            )

        # 3column별 곡선 컷
        for x in range(w):
            ys_col = np.where(mask[:, x])[0]
            if len(ys_col) == 0:
                continue

            col_top = ys_col.min()
            col_bottom = ys_col.max()
            col_height = col_bottom - col_top

            col_cut = int(col_top + col_height * ratio)
            rgba[col_cut:col_bottom, x, 3] = 0

        return rgba

    # =========================================
    # 메인 처리
    # =========================================
    def process(self, image, category: str):

        rgba = np.array(remove(image))

        policy: CutPolicy = CATEGORY_CUT_POLICY.get(
            category,
            CutPolicy(CutType.NONE)
        )

        if policy.cut_type == CutType.FACE_ONLY:

            h, w = image.shape[:2]
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_masker.face_mesh.process(rgb)

            if not results.multi_face_landmarks:
                return rgba

            landmarks = results.multi_face_landmarks[0]

            # 얼굴 타원 좌표 추출
            points = []
            for idx in self.face_masker.FACE_OVAL:
                lm = landmarks.landmark[idx]
                points.append([int(lm.x * w), int(lm.y * h)])

            points = np.array(points, dtype=np.int32)

            # 얼굴 마스크 생성
            face_mask = np.zeros((h, w), dtype=np.uint8)
            cv2.fillPoly(face_mask, [points], 255)

            # 얼굴 영역 제거
            rgba[face_mask > 0, 3] = 0

            # 얼굴 아래 제거
            ys = np.where(face_mask > 0)[0]
            if len(ys) > 0:
                face_bottom = ys.max()
                rgba[face_bottom:, :, 3] = 0

            return rgba
        # 머리 제거
        head_mask = self.face_masker.get_head_mask(image)
        rgba[head_mask > 0, 3] = 0

        # HIP_BELOW
        if policy.cut_type == CutType.HIP_BELOW:

            # TOP (dynamic)
            if policy.dynamic_ratio is not None:
                return self.process_top_dynamic(
                    image,
                    rgba,
                    ratio=policy.dynamic_ratio
                )

            # OUTER (pose 기반)
            return self.hip_cutter.cut_below_hip_contour(
                image,
                rgba,
                policy.margin_ratio
            )

        # HIP_ABOVE (하의)
        if policy.cut_type == CutType.HIP_ABOVE:
            return self.hip_cutter.cut_above_hip_contour(
                image,
                rgba,
                policy.margin_ratio
            )
        # SHORT_BOTTOM (숏팬츠 전용)
        if policy.cut_type == CutType.SHORT_BOTTOM:

            # 상체 제거
            rgba = self.hip_cutter.cut_above_hip_contour(
                image,
                rgba,
                margin_ratio=0.0
            )

            # 하체 하단 일부 제거 (무릎 아래 정리)
            h = rgba.shape[0]
            cut_line = int(h * 0.85)
            rgba[cut_line:, :, 3] = 0

            return rgba

        return rgba