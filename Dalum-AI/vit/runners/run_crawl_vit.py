import csv
import os
import cv2
import numpy as np
import io
import boto3
import gc
from dotenv import load_dotenv
from PIL import Image

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
# from recommender.style_classifier import StyleClassifier
# from vit.runners.run_db_update_vit import get_db_connection, update_style_color_material


load_dotenv()
BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def load_csv_from_s3(bucket, key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket, Key=key)
    return response["Body"].read().decode("utf-8-sig")


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


def run():

    # conn = get_db_connection()
    # cursor = conn.cursor()

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

    # style_classifier = StyleClassifier()

    metadata_rows = []
    embedding_list = []
    total_count = 0

    # S3에서 CSV 읽기
    csv_content = load_csv_from_s3(
        BUCKET_NAME,
        "crawling/musinsa_products.csv"
    )

    f = io.StringIO(csv_content)
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, 1):
        if i > 50:
            print("Test limit reached (50 images)")
            break

        product_id = row["product_id"]
        print(f"\n===== [{i}] START {product_id} =====")
        
        image = load_image_from_url(row["image_url"])
        if image is None:
            continue

        major_category = row["large_category"]
        middle_category = row["medium_category"]
        category_name = row["small_category"]

        is_model = step1.is_model_candidate(image)
        image_type = "Model" if is_model else "Product"

        filename = f"{product_id}.webp"

        # 원본 S3 업로드
        original_key = (
            f"dataset/original_images/"
            f"{image_type}/{major_category}/{middle_category}/{filename}"
        )

        success, buffer = cv2.imencode(".webp", image)
        if success:
            upload_bytes_to_s3(
                buffer.tobytes(),
                BUCKET_NAME,
                original_key,
                content_type="image/webp"
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

        success, buffer = cv2.imencode(".webp", final_img)
        if success:
            upload_bytes_to_s3(
                buffer.tobytes(),
                BUCKET_NAME,
                processed_key,
                content_type="image/webp"
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

        # # 스타일 분류
        # pil_image = Image.fromarray(
        #     cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB)
        # )
        # style = style_classifier.classify(pil_image)
        #
        # # DB 업데이트
        # update_style_color_material(cursor, conn, row["상품 URL"], material_vector, dominant_colors, style)

        print(
            f"[{'MODEL' if is_model else 'PRODUCT'}] "
            f"{filename} | {category_name} → {material_label}"
        )

        color_embedding = np.array(color_embedding, dtype=np.float32).reshape(-1)
        if material_vector is None:
            print("material_vector None → skip")
            continue
        material_vector = np.array(material_vector, dtype=np.float32).reshape(-1)

        final_embedding = np.concatenate(
            [color_embedding, material_vector],
            axis=0
        )

        embedding_list.append(final_embedding)

        metadata_rows.append({
            "index": len(embedding_list),
            "filename": filename,
            "major_category": major_category,
            "middle_category": middle_category,
            "material_label": material_label
        })

        total_count += 1
        del image, rgba, final_img
        if 'enhanced' in locals():
            del enhanced
        gc.collect()
    # cursor.close()
    # conn.close()

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
    fieldnames = [
        "index",
        "filename",
        "major_category",
        "middle_category",
        "material_label"
    ]

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