import csv
import os
import cv2
import numpy as np

from vit.preprocess.utils.image_loader import load_image_from_url
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


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(BASE_DIR, "..", "Dalum-CR", "final", "BAG.csv")

OUTPUT_BASE = os.path.join(BASE_DIR, "vit", "outputs")

ORIGINAL_DIR = os.path.join(OUTPUT_BASE, "original_images")
PROCESSED_DIR = os.path.join(OUTPUT_BASE, "processed_images")
FINAL_DIR = os.path.join(OUTPUT_BASE, "vit_output")

os.makedirs(ORIGINAL_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

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

    material_predictor = MaterialPredictor(weight_path=WEIGHT_PATH)
    material_postprocessor = MaterialPostProcessor(
        confidence_threshold=0.20,
        margin_threshold=0.03
    )

    embeddings = []
    metadata_rows = []

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):

            image = load_image_from_url(row["이미지 URL"])
            if image is None:
                continue

            filename = f"{i:06d}.png"

            major_category = row["대분류"]
            middle_category = row["중분류"]
            category_name = row["카테고리"]

            is_model = step1.is_model_candidate(image)
            image_type = "Model" if is_model else "Product"

            # 원본 저장
            original_save_dir = os.path.join(
                ORIGINAL_DIR,
                image_type,
                major_category,
                middle_category
            )
            os.makedirs(original_save_dir, exist_ok=True)
            cv2.imwrite(os.path.join(original_save_dir, filename), image)

            # 전처리
            if is_model:
                rgba = model_processor.process(image, category_name)
            else:
                rgba = product_processor.process(image)

            final_img = segmenter.center_and_pad(rgba)

            processed_save_dir = os.path.join(
                PROCESSED_DIR,
                image_type,
                major_category,
                middle_category
            )
            os.makedirs(processed_save_dir, exist_ok=True)
            cv2.imwrite(os.path.join(processed_save_dir, filename), final_img)

            # 색상 임베딩
            dominant_colors = color_extractor.extract_dominant_colors(final_img)
            color_embedding = np.array(
                build_color_embedding(dominant_colors),
                dtype=np.float32
            ).reshape(-1)

            # 재질 임베딩
            bgr_for_material = final_img[:, :, :3]
            enhanced = enhance_for_material(bgr_for_material)

            top3_materials, material_prob = material_predictor.predict_from_array(
                enhanced
            )

            material_label = material_postprocessor.select_material(
                top3_materials,
                material_prob,
                category_name
            )

            # 🔥 안전한 material_vector 처리
            if material_prob is None:
                print("material_prob None → skip")
                continue

            if isinstance(material_prob, dict):
                material_vector = np.array(
                    list(material_prob.values()),
                    dtype=np.float32
                )
            else:
                material_vector = np.array(
                    material_prob,
                    dtype=np.float32
                )

            material_vector = material_vector.reshape(-1)

            print(f"{filename} → 재질: {material_label}")

            # 최종 임베딩
            final_embedding = np.concatenate(
                [color_embedding, material_vector],
                axis=0
            )

            embeddings.append(final_embedding)

            metadata_rows.append({
                "filename": filename,
                "major_category": major_category,
                "middle_category": middle_category,
                "image_type": image_type
            })

    if len(embeddings) == 0:
        print("처리된 이미지 없음")
        return

    embeddings_array = np.vstack(embeddings)
    npy_path = os.path.join(FINAL_DIR, "embeddings.npy")
    np.save(npy_path, embeddings_array)

    print("\nNPY 저장 완료:", npy_path)
    print("Shape:", embeddings_array.shape)

    metadata_csv_path = os.path.join(FINAL_DIR, "metadata.csv")

    with open(metadata_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "filename",
                "major_category",
                "middle_category",
                "image_type"
            ]
        )
        writer.writeheader()
        writer.writerows(metadata_rows)

    print("Metadata 저장 완료:", metadata_csv_path)


if __name__ == "__main__":
    run()