import cv2
import numpy as np
from rembg import remove

from vit.preprocess.detectors.face_detector import FaceDetector
from vit.preprocess.detectors.face_contour_masker import FaceContourMasker
from vit.preprocess.detectors.pose_hip_cutter import PoseHipCutter

from vit.preprocess.utils.category_cut_policy import (
    CATEGORY_CUT_POLICY,
    CutType,
    CutPolicy,
)


def save_rgba(rgba: np.ndarray, output_path: str):
    cv2.imwrite(output_path, rgba)


class BackgroundClothingPipeline:
    def __init__(self):
        self.face_detector = FaceDetector()
        self.face_masker = FaceContourMasker()
        self.hip_cutter = PoseHipCutter()

    # 단품 이미지
    def _process_product(self, image):
        rgba = remove(image)
        return np.array(rgba)

    # 모델 이미지 (의류 전용)
    def _process_model(self, image, category: str):
        rgba = remove(image)
        rgba = np.array(rgba)

        policy: CutPolicy = CATEGORY_CUT_POLICY.get(
            category,
            CutPolicy(CutType.NONE)
        )

        # 얼굴 처리
        if policy.cut_type == CutType.FACE_ONLY:
            mask = self.face_masker.get_face_and_below_mask(image)
            rgba[mask > 0, 3] = 0
            return rgba  # 모자는 여기서 종료

        # 기본: 얼굴 + 머리 제거
        head_mask = self.face_masker.get_head_mask(image)
        rgba[head_mask > 0, 3] = 0

        # 컷 정책 적용
        if policy.cut_type == CutType.HIP_BELOW:
            rgba = self.hip_cutter.cut_below_hip_contour(
                image, rgba, policy.margin_ratio
            )

        elif policy.cut_type == CutType.HIP_ABOVE:
            rgba = self.hip_cutter.cut_above_hip_contour(
                image, rgba, policy.margin_ratio
            )

        return rgba

    # 엔트리
    def process(self, *, image, main=None, sub=None, category=None, output_path=None):
        faces = self.face_detector.detect(image)

        if len(faces) == 0:
            print("🟢 PRODUCT IMAGE")
            rgba = self._process_product(image)
        else:
            print(f"🟠 MODEL IMAGE (faces={len(faces)}) | category={category}")
            rgba = self._process_model(image, category)

        save_rgba(rgba, output_path)
