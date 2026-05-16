import os
import gc
import io
import cv2
import torch
import argparse
import numpy as np
import pandas as pd
from PIL import Image
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from dotenv import load_dotenv
from transformers import ViTModel, ViTImageProcessor

from vit.preprocess.material.predictor import MaterialPredictor
from vit.preprocess.utils.image_enhancer import enhance_for_material
from vit.utils.s3_uploader import upload_bytes_to_s3

load_dotenv()

BUCKET_NAME   = os.getenv("S3_BUCKET_NAME")
BASE_DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROCESSED_DIR = os.path.join(BASE_DIR, "vit", "outputs", "processed_images")
WEIGHT_PATH   = os.path.join(BASE_DIR, "vit", "preprocess", "material", "weights", "vits_ckpt.pth")
META_PATH     = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
OUTPUT_PATH   = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "embeddings.npy")

COLOR_DIM    = 768
SHAPE_DIM    = 768
MATERIAL_DIM = 33
EMBED_DIM    = COLOR_DIM + SHAPE_DIM + MATERIAL_DIM  # 1569
BATCH_SIZE   = 64   # GPU ViT 배치 크기 (32 → 64)
CHUNK_SIZE   = 512  # 메모리 관리를 위한 처리 단위
DEVICE       = "cuda" if torch.cuda.is_available() else "cpu"

_worker_predictor = None


def _init_material_worker(weight_path):
    global _worker_predictor
    _worker_predictor = MaterialPredictor(weight_path=weight_path)


def _predict_material_worker(args):
    vi, img_path = args
    global _worker_predictor
    try:
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            return vi, np.zeros(MATERIAL_DIM, dtype=np.float32)
        bgr = img[:, :, :3]
        enhanced = enhance_for_material(bgr)
        _, mat_vec = _worker_predictor.predict_from_array(enhanced)
        if mat_vec is None:
            return vi, np.zeros(MATERIAL_DIM, dtype=np.float32)
        if isinstance(mat_vec, dict):
            mat_vec = list(mat_vec.values())
        return vi, np.array(mat_vec, dtype=np.float32)
    except Exception:
        return vi, np.zeros(MATERIAL_DIM, dtype=np.float32)


# 이미지 경로 탐색

def find_image_path(product_id, major_category, middle_category):
    filename = f"{product_id}.webp"
    for image_type in ["Model", "Product"]:
        path = os.path.join(PROCESSED_DIR, image_type, major_category, middle_category, filename)
        if os.path.exists(path):
            return path
    return None


def _load_image_for_vit(args):
    ci, product_id, img_path = args
    if img_path is None:
        return ci, product_id, None, None
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        return ci, product_id, None, None
    pil = Image.fromarray(cv2.cvtColor(img[:, :, :3], cv2.COLOR_BGR2RGB))
    return ci, product_id, pil, img_path


# ViT 배치 추론 (GPU, 메인 프로세스)

def extract_vit_batch(images_pil, vit_model, vit_processor):
    inputs = vit_processor(images=images_pil, return_tensors="pt").to(DEVICE)
    with torch.no_grad():
        outputs    = vit_model(**inputs, output_hidden_states=True)
        color_embs = outputs.hidden_states[3][:, 0, :].cpu().numpy()
        shape_embs = outputs.hidden_states[11][:, 0, :].cpu().numpy()
    return color_embs.astype(np.float32), shape_embs.astype(np.float32)


# 메인

def run(workers: int = 8):
    if not os.path.exists(META_PATH):
        print(f"metadata.csv 없음: {META_PATH}")
        return

    print("metadata.csv 로드...")
    metadata = pd.read_csv(META_PATH)
    total = len(metadata)
    print(f"  총 {total}개  (workers={workers}, device={DEVICE})\n")

    print(f"ViT 모델 초기화...")
    vit_model     = ViTModel.from_pretrained("google/vit-base-patch16-224").to(DEVICE)
    vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
    vit_model.eval()
    print("  완료\n")

    embeddings = [None] * total
    failed     = []

    io_workers = min(workers * 2, 16)

    with ProcessPoolExecutor(
        max_workers=workers,
        initializer=_init_material_worker,
        initargs=(WEIGHT_PATH,)
    ) as mat_pool, ThreadPoolExecutor(max_workers=io_workers) as io_pool:

        for chunk_start in range(0, total, CHUNK_SIZE):
            chunk_end  = min(chunk_start + CHUNK_SIZE, total)
            chunk_rows = metadata.iloc[chunk_start:chunk_end]
            chunk_size = chunk_end - chunk_start

            # 경로 탐색 (메인 프로세스, 빠름)
            load_args = []
            for ci, (_, row) in enumerate(chunk_rows.iterrows()):
                pid = int(row["product_id"])
                maj = str(row.get("major_category", "")).replace("/", "_")
                mid = str(row.get("middle_category", "")).replace("/", "_")
                load_args.append((ci, pid, find_image_path(pid, maj, mid)))

            # Phase 1: 병렬 이미지 로딩 (스레드 풀)
            loaded = {}
            for ci, pid, pil_img, img_path in io_pool.map(
                _load_image_for_vit, load_args, chunksize=64
            ):
                loaded[ci] = (pid, pil_img, img_path)

            # 유효/실패 분리
            valid_cis = [ci for ci in range(chunk_size) if loaded[ci][1] is not None]
            for ci in range(chunk_size):
                if loaded[ci][1] is None:
                    embeddings[chunk_start + ci] = np.zeros(EMBED_DIM, dtype=np.float32)
                    failed.append(loaded[ci][0])

            if not valid_cis:
                print(f"[{chunk_end}/{total}] 유효 이미지 없음 → 건너뜀")
                continue

            # Phase 2: ViT GPU 배치 추론
            pil_imgs  = [loaded[ci][1] for ci in valid_cis]
            color_all = np.zeros((len(valid_cis), COLOR_DIM), dtype=np.float32)
            shape_all = np.zeros((len(valid_cis), SHAPE_DIM), dtype=np.float32)
            for b in range(0, len(valid_cis), BATCH_SIZE):
                c_embs, s_embs = extract_vit_batch(
                    pil_imgs[b:b + BATCH_SIZE], vit_model, vit_processor
                )
                color_all[b:b + len(c_embs)] = c_embs
                shape_all[b:b + len(s_embs)] = s_embs
            pil_imgs.clear()

            # Phase 3: 병렬 재질 예측 (프로세스 풀)
            mat_args    = [(vi, loaded[ci][2]) for vi, ci in enumerate(valid_cis)]
            mat_results = dict(mat_pool.map(_predict_material_worker, mat_args, chunksize=32))

            # 결합
            for vi, ci in enumerate(valid_cis):
                mat_vec = mat_results.get(vi, np.zeros(MATERIAL_DIM, dtype=np.float32))
                embeddings[chunk_start + ci] = np.concatenate(
                    [color_all[vi], shape_all[vi], mat_vec]
                ).astype(np.float32)

            gc.collect()
            print(f"[{chunk_end}/{total}] 처리 완료...")

    embeddings_array = np.vstack(embeddings).astype(np.float32)
    print(f"\n임베딩 shape: {embeddings_array.shape}")
    print(f"실패 수: {len(failed)}")

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    np.save(OUTPUT_PATH, embeddings_array)
    print(f"로컬 저장 완료: {OUTPUT_PATH}")

    try:
        buf = io.BytesIO()
        np.save(buf, embeddings_array)
        buf.seek(0)
        upload_bytes_to_s3(
            buf.read(), BUCKET_NAME,
            "dataset/vit_output/embeddings.npy",
            content_type="application/octet-stream"
        )
        print("S3 업로드 완료")
    except Exception as e:
        print(f"S3 업로드 실패 (무시): {e}")

    if failed:
        print(f"\n실패 product_id ({len(failed)}개): {failed[:30]}{'...' if len(failed) > 30 else ''}")

    print("\n재빌드 완료!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8, help="재질 예측 병렬 워커 수 (기본: 8)")
    args = parser.parse_args()
    run(workers=args.workers)
