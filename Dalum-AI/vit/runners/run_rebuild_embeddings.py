"""
embeddings.npy (color 768-dim ViT layer3 + material 33-dim) 재빌드 스크립트

- 로컬 vit/outputs/processed_images/{Model|Product}/{major}/{middle}/{product_id}.webp 사용
- CLIP 임베딩은 건드리지 않음
- 색상: google/vit-base-patch16-224 hidden layer 3 CLS 토큰 (768-dim)
- metadata.csv 순서와 row 수를 맞춰야 FAISS 인덱스와 정합성 유지됨
- 실패한 product는 zero vector로 채워 순서 보존
"""

import os
import gc
import io
import cv2
import torch
import numpy as np
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from transformers import ViTModel, ViTImageProcessor

from vit.preprocess.material.predictor import MaterialPredictor
from vit.preprocess.material.material_postprocessor import MaterialPostProcessor
from vit.preprocess.utils.image_enhancer import enhance_for_material
from vit.utils.s3_uploader import upload_bytes_to_s3

load_dotenv()

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
BASE_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

PROCESSED_DIR = os.path.join(BASE_DIR, "vit", "outputs", "processed_images")
WEIGHT_PATH   = os.path.join(BASE_DIR, "vit", "preprocess", "material", "weights", "vits_ckpt.pth")
META_PATH     = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
OUTPUT_PATH   = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "embeddings.npy")

COLOR_DIM    = 768  # ViT layer 3 CLS 토큰
SHAPE_DIM    = 768  # ViT layer 11 CLS 토큰
MATERIAL_DIM = 33
EMBED_DIM    = COLOR_DIM + SHAPE_DIM + MATERIAL_DIM  # 1569
BATCH_SIZE   = 32
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"


def find_image_path(product_id, major_category, middle_category):
    """Model → Product 순으로 로컬 경로 탐색"""
    filename = f"{product_id}.webp"
    for image_type in ["Model", "Product"]:
        path = os.path.join(PROCESSED_DIR, image_type, major_category, middle_category, filename)
        if os.path.exists(path):
            return path
    return None


def extract_vit_batch(images_pil, vit_model, vit_processor):
    """PIL 이미지 배치 → (color [batch,768], shape [batch,768])"""
    inputs = vit_processor(images=images_pil, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs    = vit_model(**inputs, output_hidden_states=True)
        color_embs = outputs.hidden_states[3][:, 0, :].cpu().numpy()
        shape_embs = outputs.hidden_states[11][:, 0, :].cpu().numpy()
    return color_embs.astype(np.float32), shape_embs.astype(np.float32)


def run():
    if not os.path.exists(META_PATH):
        print(f"metadata.csv 없음: {META_PATH}")
        return

    print("metadata.csv 로드...")
    metadata = pd.read_csv(META_PATH)
    total = len(metadata)
    print(f"  총 {total}개\n")

    print(f"모델 초기화... (디바이스: {DEVICE})")
    vit_model     = ViTModel.from_pretrained("google/vit-base-patch16-224").to(DEVICE)
    vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    vit_model.eval()

    material_predictor = MaterialPredictor(weight_path=WEIGHT_PATH)
    material_postproc  = MaterialPostProcessor(confidence_threshold=0.20, margin_threshold=0.03)
    print("  완료\n")

    embeddings  = []
    failed      = []
    batch_rows  = []  # (final_img, product_id, seq)
    batch_imgs  = []  # PIL images for ViT

    def flush_batch():
        if not batch_imgs:
            return
        color_embs, shape_embs = extract_vit_batch(batch_imgs, vit_model, vit_processor)

        for (final_img, product_id, seq), color_emb, shape_emb in zip(batch_rows, color_embs, shape_embs):
            try:
                bgr_for_material = final_img[:, :, :3]
                enhanced         = enhance_for_material(bgr_for_material)
                _, material_vec  = material_predictor.predict_from_array(enhanced)

                if material_vec is None:
                    material_vec = np.zeros(MATERIAL_DIM, dtype=np.float32)
                else:
                    if isinstance(material_vec, dict):
                        material_vec = list(material_vec.values())
                    material_vec = np.array(material_vec, dtype=np.float32).reshape(-1)

                embeddings.append(np.concatenate([color_emb, shape_emb, material_vec]).astype(np.float32))
            except Exception as e:
                print(f"[{seq}/{total}] {product_id} 재질 오류: {e}")
                embeddings.append(np.zeros(EMBED_DIM, dtype=np.float32))
                failed.append(product_id)

        batch_rows.clear()
        batch_imgs.clear()

    for i, row in metadata.iterrows():
        product_id      = int(row["product_id"])
        major_category  = str(row.get("major_category", "")).replace("/", "_")
        middle_category = str(row.get("middle_category", "")).replace("/", "_")
        seq             = i + 1

        try:
            img_path = find_image_path(product_id, major_category, middle_category)
            if img_path is None:
                flush_batch()
                print(f"[{seq}/{total}] {product_id} 파일 없음 → zero vector")
                embeddings.append(np.zeros(EMBED_DIM, dtype=np.float32))
                failed.append(product_id)
                continue

            final_img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
            if final_img is None:
                flush_batch()
                print(f"[{seq}/{total}] {product_id} 이미지 로드 실패 → zero vector")
                embeddings.append(np.zeros(EMBED_DIM, dtype=np.float32))
                failed.append(product_id)
                continue

            pil_img = Image.fromarray(cv2.cvtColor(final_img[:, :, :3], cv2.COLOR_BGR2RGB))
            batch_rows.append((final_img, product_id, seq))
            batch_imgs.append(pil_img)

            if len(batch_imgs) >= BATCH_SIZE:
                flush_batch()
                if seq % 1000 == 0:
                    print(f"[{seq}/{total}] 처리 중...")
                    gc.collect()

        except Exception as e:
            import traceback
            print(f"[{seq}/{total}] {product_id} 오류: {e}")
            traceback.print_exc()
            flush_batch()
            embeddings.append(np.zeros(EMBED_DIM, dtype=np.float32))
            failed.append(product_id)

    flush_batch()

    embeddings_array = np.vstack(embeddings).astype(np.float32)
    print(f"\n임베딩 shape: {embeddings_array.shape}")
    print(f"실패 수: {len(failed)}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    np.save(OUTPUT_PATH, embeddings_array)
    print(f"로컬 저장 완료: {OUTPUT_PATH}")

    try:
        npy_buffer = io.BytesIO()
        np.save(npy_buffer, embeddings_array)
        npy_buffer.seek(0)
        upload_bytes_to_s3(
            npy_buffer.read(),
            BUCKET_NAME,
            "dataset/vit_output/embeddings.npy",
            content_type="application/octet-stream"
        )
        print("S3 업로드 완료")
    except Exception as _e:
        print(f"S3 업로드 실패 (무시): {_e}")

    if failed:
        print(f"\n실패 product_id ({len(failed)}개): {failed[:30]}{'...' if len(failed) > 30 else ''}")

    print("\n재빌드 완료!")


if __name__ == "__main__":
    run()
