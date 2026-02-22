import csv
import os
import cv2

from vit.preprocess.utils.image_loader import load_image_from_url
from vit.preprocess.pipeline.step1_face_judge import Step1FaceJudge
from vit.preprocess.face.face_detector import FaceDetector
from vit.preprocess.face.face_index import FaceIndex

from vit.preprocess.processors.model_processor import ModelProcessor
from vit.preprocess.processors.product_processor import ProductProcessor
from vit.preprocess.pipeline.segmentation_processor import SegmentationProcessor
from vit.preprocess.color.color_extractor import ColorExtractor

from vit.preprocess.material.predictor import MaterialPredictor

from vit.preprocess.utils.image_enhancer import enhance_for_material
from vit.preprocess.material.material_postprocessor import MaterialPostProcessor

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(BASE_DIR, "..", "Dalum-CR", "final", "TOP.csv")

OUT_DIR = os.path.join(
    BASE_DIR, "vit", "outputs", "preprocess", "final_output"
)
os.makedirs(OUT_DIR, exist_ok=True)

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


def run():
    face_detector = FaceDetector()
    face_index = FaceIndex(FACE_INDEX_PATH)
    step1 = Step1FaceJudge(face_detector, face_index)

    model_processor = ModelProcessor()
    product_processor = ProductProcessor()
    segmenter = SegmentationProcessor()

    color_extractor = ColorExtractor(k=3)

    material_predictor = MaterialPredictor(
        weight_path=WEIGHT_PATH
    )

    material_postprocessor = MaterialPostProcessor(
        confidence_threshold=0.35
    )   

    color_rows = []

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            image = load_image_from_url(row["이미지 URL"])
            if image is None:
                continue

            category = row["카테고리"]
            is_model = step1.is_model_candidate(image)

            if is_model:
                print(f"[🟠 MODEL IMAGE] {i:06d}.png | {category}")
                rgba = model_processor.process(image, category)
            else:
                print(f"[🟢 PRODUCT IMAGE] {i:06d}.png | {category}")
                rgba = product_processor.process(image)

            final_img = segmenter.center_and_pad(rgba)

            # 색상은 원본 기준
            dominant_colors = color_extractor.extract_dominant_colors(final_img)

            # 재질은 개선 이미지 기준
            bgr_for_material = final_img[:, :, :3]

            enhanced_for_material = enhance_for_material(
                bgr_for_material
            )

            material_label = material_predictor.predict_from_array(
                enhanced_for_material,
                category
            )

            row_data = {
                "filename": f"{i:06d}.png",
                "material": material_label,
            }

            for idx, (hex_color, ratio) in enumerate(dominant_colors, start=1):
                row_data[f"dominant_color_{idx}"] = hex_color
                row_data[f"ratio_{idx}"] = round(ratio, 4)

            color_rows.append(row_data)

            filename = f"{i:06d}.png"
            cv2.imwrite(os.path.join(OUT_DIR, filename), final_img)

    csv_output_path = os.path.join(OUT_DIR, "color_material_analysis.csv")

    fieldnames = [
        "filename",
        "dominant_color_1", "ratio_1",
        "dominant_color_2", "ratio_2",
        "dominant_color_3", "ratio_3",
        "material",
    ]

    with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(color_rows)

    print(f"\nColor + Material analysis saved to {csv_output_path}")
    print("총 처리 이미지 수:", len(color_rows))



if __name__ == "__main__":
    run()
