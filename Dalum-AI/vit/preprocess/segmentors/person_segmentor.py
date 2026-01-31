import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


class PersonSegmentor:
    def __init__(self):
        base_options = python.BaseOptions(
            model_asset_path=self._download_model()
        )

        options = vision.ImageSegmenterOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            output_category_mask=True
        )

        self.segmenter = vision.ImageSegmenter.create_from_options(options)

    def _download_model(self):
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

        return model_path

    def get_person_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        result = self.segmenter.segment(mp_image)

        if result.category_mask is None:
            return None

        mask = result.category_mask.numpy_view()

        # label id: 0=background, 1=hair, 2=body, 3=face, 4=clothes (모델에 따라 약간 다를 수 있음)
        person_mask = mask != 0
        return person_mask

    def get_torso_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        h, w, _ = image_bgr.shape
        person_mask = self.get_person_mask(image_bgr)

        if person_mask is None:
            return None

        torso_band = np.zeros_like(person_mask)
        torso_band[int(h * 0.15):int(h * 0.65), :] = True

        return person_mask & torso_band
