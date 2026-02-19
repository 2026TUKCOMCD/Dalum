import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PersonSegmentor:
    def __init__(self):
        model_buffer = self._load_model_buffer()

        base_options = python.BaseOptions(
            model_asset_buffer=model_buffer   
        )

        options = vision.ImageSegmenterOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            output_category_mask=True
        )

        self.segmenter = vision.ImageSegmenter.create_from_options(options)

    # 얼굴 검증용
    def is_real_face(
        self,
        image_bgr: np.ndarray,
        face_ratio_th: float = 0.01,
        body_ratio_th: float = 0.05
    ) -> bool:

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.segmenter.segment(mp_image)

        if result.category_mask is None:
            return False

        mask = result.category_mask.numpy_view()

        total_pixels = mask.size
        if total_pixels == 0:
            return False

        face_pixels = np.sum(mask == 3)
        body_pixels = np.sum(mask == 2)

        face_ratio = face_pixels / total_pixels
        body_ratio = body_pixels / total_pixels

        return (
            face_ratio >= face_ratio_th
            and body_ratio >= body_ratio_th
        )

    # 모델을 바이트로 로드
    def _load_model_buffer(self):
        import os, urllib.request

        model_path = os.path.join(
            os.path.dirname(__file__),
            "selfie_multiclass_256x256.tflite"
        )

        if not os.path.exists(model_path):
            url = (
                "https://storage.googleapis.com/mediapipe-models/"
                "image_segmenter/selfie_multiclass_256x256/float32/1/"
                "selfie_multiclass_256x256.tflite"
            )
            urllib.request.urlretrieve(url, model_path)

        with open(model_path, "rb") as f:
            return f.read()

    # 사람 존재 비율 계산 (핵심)
    def get_person_ratio(self, image_bgr: np.ndarray) -> float:
        """
        image 안에 실제 '사람(피부/머리/몸)' 픽셀이
        얼마나 존재하는지 비율로 반환
        """

        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.segmenter.segment(mp_image)

        if result.category_mask is None:
            return 0.0

        mask = result.category_mask.numpy_view()

        total_pixels = mask.size
        if total_pixels == 0:
            return 0.0

        # label 의미:
        # 1 = hair, 2 = body, 3 = face
        person_pixels = np.sum(
            (mask == 1) |
            (mask == 2) |
            (mask == 3)
        )

        return person_pixels / total_pixels


    def get_torso_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        h, w, _ = image_bgr.shape
        person_mask = self.get_person_mask(image_bgr)

        if person_mask is None:
            return None

        torso_band = np.zeros_like(person_mask)
        torso_band[int(h * 0.15):int(h * 0.65), :] = True

        return person_mask & torso_band
