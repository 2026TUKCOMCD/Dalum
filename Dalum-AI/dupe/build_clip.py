#!/usr/bin/env python3
"""
CLIP DB 구축 - 디자인 점수(37개) + 이미지 임베딩(512차원)

metadata.csv 형식: product_id, major_category, middle_category, image_type
이미지 경로: vit/outputs/processed_images/{image_type}/{major_category}/{middle_category}/{product_id}.webp

출력:
    dupe/embeddings_clip_design.npy   (N, 37)
    dupe/embeddings_clip_image.npy    (N, 512)
"""

import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import numpy as np
import pandas as pd
import os, sys
from concurrent.futures import ProcessPoolExecutor, as_completed

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
AI_BASE_DIR   = os.path.dirname(BASE_DIR)

METADATA_PATH    = os.path.join(AI_BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
PROCESSED_DIR    = os.path.join(AI_BASE_DIR, "vit", "outputs", "processed_images")
CLIP_DESIGN_PATH = os.path.join(BASE_DIR, "embeddings_clip_design.npy")
CLIP_IMAGE_PATH  = os.path.join(BASE_DIR, "embeddings_clip_image.npy")

NUM_WORKERS    = 6
GPU_BATCH_SIZE = 64

# ==================== 디자인 프롬프트 (37개) ====================

DESIGN_PROMPTS = {
    "solid"        : "a solid color clothing with no pattern",
    "color_block"  : "a clothing with color block design",
    "gradient"     : "a clothing with gradient or ombre color effect",
    "striped"      : "a clothing with stripe pattern",
    "checkered"    : "a clothing with check or plaid pattern",
    "argyle"       : "a clothing with argyle diamond pattern",
    "houndstooth"  : "a clothing with houndstooth pattern",
    "polka_dot"    : "a clothing with polka dot pattern",
    "geometric"    : "a clothing with geometric shapes pattern",
    "floral"       : "a clothing with floral or flower pattern",
    "paisley"      : "a clothing with paisley or abstract pattern",
    "animal_print" : "a clothing with animal print like leopard or zebra",
    "camouflage"   : "a clothing with camouflage pattern",
    "tie_dye"      : "a clothing with tie dye pattern",
    "logo_text"    : "a clothing with logo or text print",
    "graphic"      : "a clothing with graphic or illustration print",
    "character"    : "a clothing with cartoon character, mascot, or animal graphic print",
    "heart"        : "a clothing with heart shape print",
    "star"         : "a clothing with star shape print",
    "embroidery"   : "a clothing with embroidery or embroidered detail",
    "rhinestone"   : "a clothing with rhinestones studs or jewel details",
    "ribbon_bow"   : "a clothing with ribbon or bow detail",
    "fringe"       : "a clothing with fringe or tassel detail",
    "metallic"     : "a clothing with shiny metallic sequin or glitter",
    "pleated"      : "a clothing with pleated or ruffle details",
    "varsity"      : "a varsity or stadium jacket with contrast sleeves",
    "washed"       : "a washed distressed or vintage treated clothing",
    "denim"        : "a denim clothing like jeans or denim jacket",
    "knit"         : "a knit or cable knit sweater clothing",
    "leather"      : "a clothing made of leather or faux leather",
    "fur"          : "a clothing made of fluffy fur or faux fur",
    "fleece"       : "a clothing made of cozy fleece material",
    "velvet"       : "a clothing made of velvet or velour fabric",
    "silk_satin"   : "a clothing made of glossy silk or satin fabric",
    "linen"        : "a clothing made of breathable linen fabric",
    "sheer"        : "a sheer or transparent mesh clothing",
    "lace"         : "a clothing with lace detail or lace fabric",
}

DESIGN_NAMES = list(DESIGN_PROMPTS.keys())
DESIGN_TEXTS = list(DESIGN_PROMPTS.values())


def build_image_path(row):
    return os.path.join(
        PROCESSED_DIR,
        str(row["image_type"]),
        str(row["major_category"]),
        str(row["middle_category"]),
        f"{int(row['product_id'])}.webp",
    )


# ==================== 워커 함수 (프로세스당 CLIP 1개 로드) ====================

def process_chunk(args):
    """
    chunk_id, rows_list(dict list) → (chunk_id, image_embs, design_embs)
    rows_list: [{"idx": i, "image_type":..., ...}, ...]
    """
    chunk_id, rows_list, processed_dir, design_texts, design_names = args

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
        img_path = os.path.join(
            processed_dir,
            str(row["image_type"]),
            str(row["major_category"]),
            str(row["middle_category"]),
            f"{int(row['product_id'])}.webp",
        )

        if not os.path.exists(img_path):
            results[orig_idx] = (
                np.zeros(512, dtype="float32"),
                np.ones(n_design, dtype="float32") / n_design,
            )
            continue

        try:
            img = Image.open(img_path).convert("RGB")
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


# ==================== 메인 ====================

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

    args_list = [
        (cid, chunk, PROCESSED_DIR, DESIGN_TEXTS, DESIGN_NAMES)
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
    sys.path.insert(0, AI_BASE_DIR)
    build_clip_database()
