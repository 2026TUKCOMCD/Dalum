#!/usr/bin/env python3
import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import numpy as np
import pandas as pd
import os, sys
import boto3
from io import BytesIO
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
AI_BASE_DIR   = os.path.dirname(BASE_DIR)

sys.path.insert(0, AI_BASE_DIR)
from dupe.prompts import DESIGN_NAMES, DESIGN_TEXTS

METADATA_PATH    = os.path.join(AI_BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
PROCESSED_DIR    = os.path.join(AI_BASE_DIR, "vit", "outputs", "processed_images")
CLIP_DESIGN_PATH = os.path.join(BASE_DIR, "embeddings_clip_design.npy")
CLIP_IMAGE_PATH  = os.path.join(BASE_DIR, "embeddings_clip_image.npy")

NUM_WORKERS    = 6
GPU_BATCH_SIZE = 64


def build_image_path(row):
    return os.path.join(
        PROCESSED_DIR,
        str(row["image_type"]),
        str(row["major_category"]),
        str(row["middle_category"]),
        f"{int(row['product_id'])}.webp",
    )


# 워커 함수 (프로세스당 CLIP 1개 로드)

def process_chunk(args):
    chunk_id, rows_list, s3_bucket, s3_prefix, design_texts, design_names = args
    load_dotenv()
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    device = "cpu"  # 멀티프로세스는 CPU 사용
    clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    clip_model.eval()

    # 텍스트 임베딩 캐싱
    with torch.no_grad():
        text_inputs = clip_processor(text=design_texts, return_tensors="pt", padding=True).to(device)
        text_out    = clip_model.get_text_features(**text_inputs)
        if not isinstance(text_out, torch.Tensor):
            text_out = text_out.pooler_output
        cached_text_embs = F.normalize(text_out, dim=-1)

    n_design  = len(design_names)
    n_total   = len(rows_list)
    results   = {}  # idx → (image_emb, design_emb)
    processed = 0

    batch_imgs = []
    batch_idxs = []

    def flush():
        if not batch_imgs:
            return
        inputs = clip_processor(images=batch_imgs, return_tensors="pt", padding=True).to(device)
        with torch.no_grad():
            img_feats = clip_model.get_image_features(**inputs)
            if not isinstance(img_feats, torch.Tensor):
                img_feats = img_feats.pooler_output
            img_embs = F.normalize(img_feats, dim=-1)
            logits   = (img_embs @ cached_text_embs.T) * 100
            probs    = F.softmax(logits, dim=-1)

        for bidx, (e, p) in zip(batch_idxs, zip(img_embs.cpu().numpy(), probs.cpu().numpy())):
            results[bidx] = (e.astype("float32"), p.astype("float32"))

        batch_imgs.clear()
        batch_idxs.clear()

    for row in rows_list:
        orig_idx = row["orig_idx"]
        s3_key = (f"{s3_prefix}/{row['image_type']}/{row['major_category']}"
                  f"/{row['middle_category']}/{int(row['product_id'])}.webp")

        try:
            resp = s3.get_object(Bucket=s3_bucket, Key=s3_key)
            buf  = resp["Body"].read()
            img  = Image.open(BytesIO(buf)).convert("RGB")
            batch_imgs.append(img)
            batch_idxs.append(orig_idx)
        except Exception:
            results[orig_idx] = (
                np.zeros(512, dtype="float32"),
                np.ones(n_design, dtype="float32") / n_design,
            )
            continue

        if len(batch_imgs) >= GPU_BATCH_SIZE:
            flush()

        processed += 1
        if processed % 1000 == 0:
            print(f"  [워커 {chunk_id}] {processed}/{n_total} 완료...")

    flush()

    print(f"  [워커 {chunk_id}] 완료 ({n_total}개)")
    return chunk_id, results


# 메인

def build_clip_database():
    if not os.path.exists(METADATA_PATH):
        print(f"metadata.csv 없음: {METADATA_PATH}")
        sys.exit(1)

    metadata = pd.read_csv(METADATA_PATH)
    n_total  = len(metadata)
    print(f"총 {n_total}개 / 워커 {NUM_WORKERS}개로 병렬 처리 시작...\n")

    # metadata를 NUM_WORKERS 청크로 분할
    rows_list = []
    for i, row in metadata.iterrows():
        d = row.to_dict()
        d["orig_idx"] = i
        rows_list.append(d)

    chunk_size = (n_total + NUM_WORKERS - 1) // NUM_WORKERS
    chunks = [rows_list[i:i + chunk_size] for i in range(0, n_total, chunk_size)]

    load_dotenv()
    s3_bucket = os.getenv("S3_BUCKET_NAME", "dalum-storage")
    s3_prefix = "outputs_final/processed_images"
    args_list = [
        (cid, chunk, s3_bucket, s3_prefix, DESIGN_TEXTS, DESIGN_NAMES)
        for cid, chunk in enumerate(chunks)
    ]

    # 결과 수집
    all_results = {}  # orig_idx → (image_emb, design_emb)

    with ProcessPoolExecutor(max_workers=NUM_WORKERS) as executor:
        futures = {executor.submit(process_chunk, args): args[0] for args in args_list}
        for future in as_completed(futures):
            chunk_id = futures[future]
            try:
                _, chunk_results = future.result()
                all_results.update(chunk_results)
            except Exception as e:
                print(f"  [워커 {chunk_id}] 오류: {e}")

    # orig_idx 순서대로 정렬하여 배열 구성
    image_embs  = []
    design_embs = []
    for i in range(n_total):
        if i in all_results:
            ie, de = all_results[i]
        else:
            ie = np.zeros(512, dtype="float32")
            de = np.ones(len(DESIGN_NAMES), dtype="float32") / len(DESIGN_NAMES)
        image_embs.append(ie)
        design_embs.append(de)

    image_result  = np.array(image_embs,  dtype="float32")
    design_result = np.array(design_embs, dtype="float32")

    np.save(CLIP_IMAGE_PATH,  image_result)
    np.save(CLIP_DESIGN_PATH, design_result)

    print(f"\n완료!")
    print(f"  embeddings_clip_image.npy  : {image_result.shape}")
    print(f"  embeddings_clip_design.npy : {design_result.shape}")


if __name__ == "__main__":
    build_clip_database()
