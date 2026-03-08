import os
import cv2
import numpy as np
import io
import csv
import gc
import psycopg2.extras
from dotenv import load_dotenv

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

from vit.runners.run_db_update_vit import get_db_connection

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


def run():
    # DB 연결 
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cursor.execute("""
        SELECT product_id,
               image_url,
               large_category,
               medium_category,
               small_category
        FROM product
    """)

    rows = cursor.fetchall()

    # 모델 초기화
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

    # 루프 시작
    for i, row in enumerate(rows, 1):

        # t2.small 안정 테스트
        if i > 50:
            print("Test limit reached (50 images)")
            break

        product_id = row["product_id"]
        image_url = row["image_url"]
        major_category = row["large_category"]
        middle_category = row["medium_category"]
        category_name = row["small_category"]
        
        if major_category:
            major_category = major_category.replace("/", "_")

        if middle_category:
            middle_category = middle_category.replace("/", "_")
            
        print(f"\n===== [{i}] START {product_id} =====")
        
        image = load_image_from_url(image_url)
        if image is None:
            continue

        is_model = step1.is_model_candidate(image)
        image_type = "Model" if is_model else "Product"

        filename = f"{product_id}.webp"

        # 원본 S3 업로드
        original_key = (
            f"dataset/original_images/"
            f"{image_type}/{major_category}/{middle_category}/{filename}"
        )

        success, buffer = cv2.imencode(
            ".webp",
            image,
            [cv2.IMWRITE_WEBP_QUALITY, 85]
        )
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

        # 색상 & 재질 임베딩
        dominant_colors = color_extractor.extract_dominant_colors(final_img)
        color_embedding = np.array(
            build_color_embedding(dominant_colors),
            dtype=np.float32
        ).reshape(-1)

        enhanced = enhance_for_material(final_img[:, :, :3])

        top3_materials, material_vector = material_predictor.predict_from_array(
            enhanced
        )

        if material_vector is None:
            continue

        material_vector = np.array(
            material_vector,
            dtype=np.float32
        ).reshape(-1)
        
        final_embedding = np.concatenate(
            [color_embedding, material_vector],
            axis=0
        )

        embedding_list.append(final_embedding)

        metadata_rows.append({
            "index": len(embedding_list),
            "product_id": product_id,
            "major_category": major_category,
            "middle_category": middle_category
        })
        total_count += 1
        
        del image, rgba, final_img, enhanced
        gc.collect()

    cursor.close()
    conn.close()

    if len(embedding_list) == 0:
        print("처리된 이미지가 없습니다.")
        return
    
    embedding_array = np.vstack(embedding_list)
        # # 스타일 분류
        # pil_image = Image.fromarray(
        #     cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB)
        # )
        # style = style_classifier.classify(pil_image)
        #
        # # DB 업데이트
        # update_style_color_material(cursor, conn, row["상품 URL"], material_vector, dominant_colors, style)


    # embedimgs.npy 저장
    npy_buffer = io.BytesIO()
    np.save(npy_buffer, embedding_array)
    npy_buffer.seek(0)

    upload_bytes_to_s3(
        npy_buffer.read(),
        BUCKET_NAME,
        "dataset/vit_output/embeddings.npy",
        content_type="application/octet-stream"
    )

    # metadata.csv 저장
    csv_buffer = io.StringIO()
    fieldnames = [
        "index",
        "product_id",
        "major_category",
        "middle_category",
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