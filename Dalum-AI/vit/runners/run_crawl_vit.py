import csv
import os
import cv2
import json
import numpy as np
import io
from dotenv import load_dotenv

import psycopg2

from vit.utils.s3_uploader import upload_bytes_to_s3

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


load_dotenv()
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CSV_PATH = os.path.join(BASE_DIR, "..", "Dalum-CR", "final", "TOP.csv")

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

    conn = get_db_connection()
    cursor = conn.cursor()

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

    metadata_rows = [] 
    embedding_list = []
    total_count = 0

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):

            image = load_image_from_url(row["이미지 URL"])
            if image is None:
                continue

            major_category = row["대분류"]
            middle_category = row["중분류"]
            category_name = row["카테고리"]

            is_model = step1.is_model_candidate(image)
            image_type = "Model" if is_model else "Product"

            filename = f"{i:06d}.png"

            # 원본 S3 업로드
            original_key = (
                f"dataset/original_images/"
                f"{image_type}/{major_category}/{middle_category}/{filename}"
            )

            success, buffer = cv2.imencode(".png", image)
            if success:
                upload_bytes_to_s3(
                    buffer.tobytes(),
                    BUCKET_NAME,
                    original_key,
                    content_type="image/png"
                )

            # 전처리
            if is_model:
                rgba = model_processor.process(image, category_name)
            else:
                rgba = product_processor.process(image)

            final_img = segmenter.center_and_pad(rgba)

            # 전처리 이미지 S3 업로드
            processed_key = (
                f"dataset/processed_images/"
                f"{image_type}/{major_category}/{middle_category}/{filename}"
            )

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

            # 재질 임베딩
            bgr_for_material = final_img[:, :, :3]
            enhanced = enhance_for_material(bgr_for_material)

            top3_materials, material_vector = material_predictor.predict_from_array(
                enhanced
            )

            material_label = material_postprocessor.select_material(
                top3_materials,
                material_vector,
                category_name
            )

            # DB 업데이트
            dominant_color_list = [
                {"hex": hex_color, "ratio": float(round(ratio, 4))}
                for hex_color, ratio in dominant_colors
            ]
            cursor.execute(
                """
                UPDATE product
                SET material_vector = %s,
                    dominant_colors = %s
                WHERE purchase_link = %s
                """,
                (
                    json.dumps(material_vector),
                    json.dumps(dominant_color_list),
                    row["상품 URL"],
                ),
            )
            conn.commit()

            # 한 줄 로그 출력
            log_type = "MODEL" if is_model else "PRODUCT"
            print(
                f"[{log_type}] {filename} | {category_name} → {material_label}"
            )

            final_embedding = np.concatenate([
                np.array(color_embedding),
                np.array(material_vector)
            ])

            embedding_list.append(final_embedding)

            metadata_rows.append({
                "index": len(embedding_list),
                "filename": filename,
                "major_category": major_category,
                "middle_category": middle_category,
                "material_label": material_label
            })

            total_count += 1
    cursor.close()
    conn.close()

    if len(embedding_list) == 0:
        print("처리된 이미지가 없습니다.")
        return
    
    embedding_array = np.vstack(embedding_list)

    npy_buffer = io.BytesIO()
    np.save(npy_buffer, embedding_array)
    npy_buffer.seek(0)

    upload_bytes_to_s3(
        npy_buffer.read(),
        BUCKET_NAME,
        "dataset/vit_output/embeddings.npy",
        content_type="application/octet-stream"
    )

    csv_buffer = io.StringIO()
    fieldnames = ["index", "filename", "major_category", "middle_category", "material_label"]

    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(metadata_rows)

    upload_bytes_to_s3(
        csv_buffer.getvalue().encode("utf-8"),
        BUCKET_NAME,
        "dataset/vit_output/metadata.csv",
        content_type="text/csv"
    )

    print("\n===================================")
    print(f"완료 | 총 처리 이미지 수: {total_count}")


if __name__ == "__main__":
    run()