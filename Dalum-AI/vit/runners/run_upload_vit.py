import os
import torch
import numpy as np
from dotenv import load_dotenv
import cv2
from PIL import Image
from transformers import ViTModel, ViTImageProcessor

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


from vit.preprocess.material.predictor import MaterialPredictor
from vit.preprocess.material.material_postprocessor import MaterialPostProcessor
from vit.preprocess.utils.image_enhancer import enhance_for_material

from recommender.style_classifier import StyleClassifier


load_dotenv()

# 대분류 → 크롭 정책 폴백
_MAJOR_TO_DEFAULT_MIDDLE = {
    "TOP"   : "기타 상의",
    "OUTER" : "기타 아우터",
    "BOTTOM": "기타 팬츠",
    "DRESS" : "원피스",
    "HAT"   : "기타 모자",
    "BAG"   : "",
    "SHOES" : "",
}

# 영문 중분류(metadata) -> 한국어 크롭 카테고리
_MIDDLE_TO_CROP_CATEGORY = {
    # TOP
    "HOODIE"     : "후드",
    "SWEATSHIRT" : "스웨트 셔츠",
    "TSHIRT"     : "티셔츠",
    "LSHIRT"     : "긴소매 티셔츠",
    "KNIT"       : "니트",
    # OUTER
    "PADDING"    : "경량 패딩",
    "COAT"       : "코트",
    "JACKET"     : "기타 자켓",
    "JUMPER"     : "기타 점퍼",
    "VEST"       : "베스트",
    "CARDIGAN"   : "가디건",
    "ZIP_UP"     : "집업",
    "ETC_OUTER"  : "기타 아우터",
    # BOTTOM
    "SLACKS"     : "슬랙스",
    "PANTS"      : "코튼 팬츠",
    "SHORT_PANTS": "숏 팬츠",
    "DENIM"      : "데님 팬츠",
    "ETC_BOTTOM" : "기타 팬츠",
    "WAIST"      : "기타 팬츠",
    # DRESS
    "ONE_PIECE"  : "원피스",
    # HAT
    "CAP"        : "볼캡",
    "BEANIE"     : "비니",
    "ETC_HAT"    : "기타 모자",
    "BERET"      : "베레모",
    "BALACLAVA"  : "바라클라바",
    "FEDORA"     : "페도라",
    "TROOPER"    : "트루퍼",
}

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

_vit_device       = "cuda" if torch.cuda.is_available() else "cpu"
vit_color_model = ViTModel.from_pretrained(
    "google/vit-base-patch16-224",
    local_files_only=True
).to(_vit_device)

vit_color_processor = ViTImageProcessor.from_pretrained(
    "google/vit-base-patch16-224",
    local_files_only=True
)
vit_color_model.eval()

material_predictor = MaterialPredictor(weight_path=WEIGHT_PATH)
material_postprocessor = MaterialPostProcessor(
    confidence_threshold=0.20,
    margin_threshold=0.03
)

style_classifier = StyleClassifier()


def process_upload_image(s3_key: str, category_hint: str = None, image_bytes: bytes = None) -> dict:
    """
    Args:
        s3_key (str): S3 original 이미지 key
        category_hint (str): 선택적 카테고리 힌트
        image_bytes (bytes): 직접 전달된 이미지 바이트 (S3 다운로드 생략)
    """

    if image_bytes is not None:
        img_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    else:
        image = download_image_from_s3(BUCKET_NAME, s3_key)

    if image is None:
        raise ValueError("이미지를 불러오지 못했습니다.")

    # 카테고리 감지를 크롭보다 먼저 수행 (원본 이미지 기준)
    from dupe.dupe import detect_major_category, detect_middle_category, extract_clip_features
    pil_raw = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # CLIP 임베딩 한 번만 추출 -> 대분류 + 중분류 동시 사용
    clip_raw_emb, _, _ = extract_clip_features(pil_raw)
    detected_category = category_hint or detect_major_category(clip_emb=clip_raw_emb)
    middle_category   = detect_middle_category(clip_raw_emb, detected_category)
    crop_category     = _MIDDLE_TO_CROP_CATEGORY.get(middle_category) or _MAJOR_TO_DEFAULT_MIDDLE.get(detected_category, "")

    print(f"[카테고리] 대분류={detected_category} 중분류={middle_category} 크롭={crop_category}")

    # 모델 / 제품 판별 → 감지된 카테고리로 크롭 정책 결정
    is_model = step1.is_model_candidate(image)

    if is_model:
        rgba = model_processor.process(image, crop_category)
    else:
        rgba = product_processor.process(image)

    final_img = segmenter.center_and_pad(rgba)

    # Processed 이미지 S3 저장 (PNG로 전환)
    filename = os.path.basename(s3_key)
    name_without_ext = os.path.splitext(filename)[0]

    processed_key = f"user_upload/processed/{name_without_ext}.png"

    success, buffer = cv2.imencode(".png", final_img)

    if success:
        try:
            upload_bytes_to_s3(
                buffer.tobytes(),
                BUCKET_NAME,
                processed_key,
                content_type="image/png"
            )
        except Exception as _e:
            print(f"처리 이미지 S3 업로드 실패 (무시): {_e}")

    # 의상 픽셀 평균 LAB 색상 추출 (명도·채도·색상 직접 비교용)
    if final_img.shape[2] == 4:
        _alpha_mask = final_img[:, :, 3] > 30
        _bgr_pixels = final_img[:, :, :3][_alpha_mask]
    else:
        _gray = cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2GRAY)
        _bgr_pixels = final_img[:, :, :3][_gray < 240]

    if len(_bgr_pixels) >= 100:
        # 상위 15% 밝기 픽셀 제거 — 광택 소재(가죽 등) 스페큘러 하이라이트 제거
        _gray_vals = (0.299 * _bgr_pixels[:, 2].astype(np.float32)
                      + 0.587 * _bgr_pixels[:, 1].astype(np.float32)
                      + 0.114 * _bgr_pixels[:, 0].astype(np.float32))
        _bright_thr = float(np.percentile(_gray_vals, 85))
        _filtered   = _bgr_pixels[_gray_vals <= _bright_thr]
        if len(_filtered) < 50:
            _filtered = _bgr_pixels  # 픽셀 너무 적으면 원본 사용
        _median_bgr     = np.median(_filtered, axis=0).astype(np.float32)
        _median_bgr_img = _median_bgr.reshape(1, 1, 3).astype(np.uint8)
        _median_lab_img = cv2.cvtColor(_median_bgr_img, cv2.COLOR_BGR2LAB)
        dominant_lab = [
            float(_median_lab_img[0, 0, 0]) * 100.0 / 255.0,
            float(_median_lab_img[0, 0, 1]) - 128.0,
            float(_median_lab_img[0, 0, 2]) - 128.0,
        ]
    else:
        dominant_lab = [50.0, 0.0, 0.0]

    print(f"[COLOR-LAB] L={dominant_lab[0]:.1f}  a={dominant_lab[1]:.1f}  b={dominant_lab[2]:.1f}")

    # 색상(layer3) + 형태(layer11) 임베딩 — ViT CLS 토큰
    pil_for_vit = Image.fromarray(cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB))
    vit_inputs  = vit_color_processor(images=pil_for_vit, return_tensors="pt").to(_vit_device)
    with torch.no_grad():
        vit_out         = vit_color_model(**vit_inputs, output_hidden_states=True)
        color_embedding = vit_out.hidden_states[3][:, 0, :].cpu().numpy().squeeze().tolist()
        shape_embedding = vit_out.hidden_states[11][:, 0, :].cpu().numpy().squeeze().tolist()

    dominant_color_list = []

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

    # 스타일 분류
    pil_image = Image.fromarray(cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB))
    style = style_classifier.classify(pil_image)

    # CLIP 임베딩 추출 (크롭된 이미지 기준)
    pil_for_clip = Image.fromarray(cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB))
    clip_emb, _, clip_design_probs = extract_clip_features(pil_for_clip)

    # JSON 반환
    return {
        "category": detected_category,
        "middle_category": middle_category,
        "style": style,
        "embedding": {
            "color": color_embedding,
            "shape": shape_embedding,
            "material": material_vector
        },
        "clip_embedding": clip_emb[0].tolist(),
        "clip_design_probs": clip_design_probs.tolist(),
        "lab_color": dominant_lab,
        "meta": {
            "dominant_colors": dominant_color_list,
            "material_label": material_label,
            "is_model_image": bool(is_model),
            "s3_original_key": s3_key,
            "processed_s3_key": processed_key
        }
    }