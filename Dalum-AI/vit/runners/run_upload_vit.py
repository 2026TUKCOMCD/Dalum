# vit/runners/run_upload_vit.py

import os
import numpy as np
from dotenv import load_dotenv
import cv2

from vit.utils.s3_uploader import (
    download_image_from_s3,
    upload_bytes_to_s3
)

from vit.preprocess.pipeline.step1_face_judge import Step1FaceJudge
from vit.preprocess.face.face_detector import FaceDetector
from vit.preprocess.face.face_index import FaceIndex

from vit.preprocess.processors.model_processor import ModelProcessor
from vit.preprocess.processors.product_processor import ProductProcessor
from vit.preprocess.pipeline.segmentation_processor import SegmentationProcessor

from vit.preprocess.color.color_extractor import ColorExtractor
from vit.preprocess.color.color_embedding import build_color_embedding

from vit.preprocess.material.predictor import MaterialPredictor
from vit.preprocess.material.material_postprocessor import MaterialPostProcessor
from vit.preprocess.utils.image_enhancer import enhance_for_material


load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

FACE_INDEX_PATH = os.path.join(
    BASE_DIR, "vit", "preprocess", "datasets", "face_index.json"
)

WEIGHT_PATH = os.path.join(
    BASE_DIR,
    "vit",
    "preprocess",
    "material",
    "weights",
    "vits_ckpt.pth",
)

# 서버 시작 시 1회 모델 초기화
face_detector = FaceDetector()
face_index = FaceIndex(FACE_INDEX_PATH)
step1 = Step1FaceJudge(face_detector, face_index)

model_processor = ModelProcessor()
product_processor = ProductProcessor()
segmenter = SegmentationProcessor()

color_extractor = ColorExtractor(k=3)

material_predictor = MaterialPredictor(weight_path=WEIGHT_PATH)
material_postprocessor = MaterialPostProcessor(
    confidence_threshold=0.20,
    margin_threshold=0.03
)


def process_upload_image(s3_key: str, category_hint: str = None) -> dict:
    """
    Args:
        s3_key (str): S3 original 이미지 key
        category_hint (str): 선택적 카테고리 힌트
    """

    # S3 이미지 다운로드
    image = download_image_from_s3(BUCKET_NAME, s3_key)

    if image is None:
        raise ValueError("S3에서 이미지를 불러오지 못했습니다.")

    # 모델 / 제품 판별
    is_model = step1.is_model_candidate(image)

    if is_model:
        rgba = model_processor.process(image, category_hint or "")
    else:
        rgba = product_processor.process(image)

    # enter & Pad
    final_img = segmenter.center_and_pad(rgba)

    # Processed 이미지 S3 저장 (PNG로 전환)
    filename = os.path.basename(s3_key)
    name_without_ext = os.path.splitext(filename)[0]

    processed_key = f"user_upload/processed/{name_without_ext}.png"

    success, buffer = cv2.imencode(".png", final_img)

    if success:
        upload_bytes_to_s3(
            buffer.tobytes(),
            BUCKET_NAME,
            processed_key,
            content_type="image/png"
        )

    # 색상 임베딩
    dominant_colors = color_extractor.extract_dominant_colors(final_img)
    color_embedding = build_color_embedding(dominant_colors)

    dominant_color_list = [
        {"hex": hex_color, "ratio": float(round(ratio, 4))}
        for hex_color, ratio in dominant_colors
    ]

    # 재질 임베딩
    bgr_for_material = final_img[:, :, :3]
    enhanced = enhance_for_material(bgr_for_material)

    top3_materials, material_vector = material_predictor.predict_from_array(
        enhanced
    )

    material_label = material_postprocessor.select_material(
        top3_materials,
        material_vector,
        category_hint or ""
    )

    # JSON 반환
    return {
        "category": category_hint or "UNKNOWN",
        "embedding": {
            "color": color_embedding,
            "material": material_vector
        },
        "meta": {
            "dominant_colors": dominant_color_list,
            "material_label": material_label,
            "is_model_image": bool(is_model),
            "s3_original_key": s3_key,
            "processed_s3_key": processed_key
        }
    }