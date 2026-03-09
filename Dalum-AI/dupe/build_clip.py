#!/usr/bin/env python3
"""
CLIP 디자인 DB 구축 - 디자인 점수(37개) + 이미지 임베딩(512차원) 동시 저장

출력:
    embeddings_clip_design.npy   (N, 37)  - 디자인 점수
    embeddings_clip_image.npy    (N, 512) - 이미지 임베딩 (색상+위치+디테일)

사용법:
    python build_clip_design.py
    python build_clip_design.py --batch 256
"""

import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import numpy as np
import pandas as pd
import os, sys, time, json, glob

# ==================== 설정 ====================

BASE_DIR           = os.path.dirname(os.path.abspath(__file__))
METADATA_PATH      = os.path.join(os.path.expanduser('~'), 'backups', 'embeddings_metadata.csv')
CLIP_DESIGN_PATH   = os.path.join(BASE_DIR, 'embeddings_clip_design.npy')
CLIP_IMAGE_PATH    = os.path.join(BASE_DIR, 'embeddings_clip_image.npy')
CLIP_LABEL_PATH    = os.path.join(BASE_DIR, 'embeddings_clip_design_labels.txt')
SKIP_LOG_PATH      = os.path.join(BASE_DIR, 'build_clip_design_skip.jsonl')
LOCAL_IMAGE_DIR    = os.path.expanduser('~/processed/processed')
GPU_BATCH_SIZE     = 128
SAVE_EVERY         = 5000

for i, arg in enumerate(sys.argv[1:], 1):
    if arg == '--batch' and i < len(sys.argv) - 1:
        GPU_BATCH_SIZE = int(sys.argv[i + 1])

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
N_DESIGNS    = len(DESIGN_NAMES)

# ==================== 초기화 ====================

print(f"\n{'='*55}")
print(f"  🚀 CLIP 디자인 DB 구축 (디자인 + 이미지 임베딩)")
print(f"{'='*55}")
print(f"  이미지 경로  : {LOCAL_IMAGE_DIR}")
print(f"  GPU 배치     : {GPU_BATCH_SIZE}")
print(f"  디자인 항목  : {N_DESIGNS}개")
print(f"  출력 1       : {CLIP_DESIGN_PATH}  (N, {N_DESIGNS})")
print(f"  출력 2       : {CLIP_IMAGE_PATH}  (N, 512)")
print(f"{'='*55}\n")

print("0️⃣  로컬 이미지 목록 로드...")
png_files = set(os.path.basename(f) for f in glob.glob(f"{LOCAL_IMAGE_DIR}/*.png"))
print(f"   ✅ {len(png_files):,}개\n")
if not png_files:
    print(f"❌ 이미지 없음: {LOCAL_IMAGE_DIR}")
    sys.exit(1)

print("1️⃣  CLIP 모델 로드...")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"   디바이스: {device}")
clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
with torch.no_grad():
    text_inputs      = clip_processor(text=DESIGN_TEXTS, return_tensors="pt", padding=True).to(device)
    cached_text_embs = F.normalize(clip_model.get_text_features(**text_inputs), dim=-1)
print(f"   ✅ 완료\n")

print("2️⃣  메타데이터 로드...")
metadata = pd.read_csv(METADATA_PATH)
n_total  = len(metadata)
print(f"   ✅ {n_total:,}개\n")

# ==================== 이어하기 ====================

# 디자인 점수
if os.path.exists(CLIP_DESIGN_PATH):
    existing_design = np.load(CLIP_DESIGN_PATH)
    if existing_design.shape[1] != N_DESIGNS:
        print(f"⚠️  디자인 차원 불일치 ({existing_design.shape[1]} → {N_DESIGNS}) → 처음부터\n")
        start_idx      = 0
        all_design     = []
        all_image_embs = []
    else:
        start_idx      = len(existing_design)
        all_design     = list(existing_design)
        # 이미지 임베딩도 이어하기
        if os.path.exists(CLIP_IMAGE_PATH):
            existing_image = np.load(CLIP_IMAGE_PATH)
            all_image_embs = list(existing_image)
        else:
            all_image_embs = []
            start_idx = 0  # 이미지 임베딩 없으면 처음부터
        print(f"⏩ 이어하기: {start_idx:,}개 완료, {n_total-start_idx:,}개 남음\n")
else:
    start_idx      = 0
    all_design     = []
    all_image_embs = []
    print(f"🆕 처음부터: {n_total:,}개\n")

# ==================== 추론 루프 ====================

print(f"3️⃣  추론 시작...\n")

skip_log   = open(SKIP_LOG_PATH, 'a', buffering=1)
skip_count = 0
t_start    = time.time()
batch_imgs = []
batch_idxs = []

def flush_batch():
    if not batch_imgs:
        return
    inputs = clip_processor(images=batch_imgs, return_tensors="pt", padding=True).to(device)
    with torch.no_grad():
        # 이미지 임베딩 (512차원, L2 정규화)
        img_embs = F.normalize(clip_model.get_image_features(**inputs), dim=-1)
        # 디자인 점수
        logits   = (img_embs @ cached_text_embs.T) * 100
        probs    = F.softmax(logits, dim=-1)

    img_embs_np = img_embs.cpu().numpy().astype(np.float32)
    probs_np    = probs.cpu().numpy().astype(np.float32)

    for ie, pr in zip(img_embs_np, probs_np):
        all_image_embs.append(ie)
        all_design.append(pr)

    batch_imgs.clear()
    batch_idxs.clear()

for i in range(start_idx, n_total):
    fn         = os.path.basename(metadata.iloc[i]['saved_path'])
    local_path = os.path.join(LOCAL_IMAGE_DIR, fn)

    if fn not in png_files:
        skip_count += 1
        skip_log.write(json.dumps({
            'db_idx': int(i), 'filename': fn,
            'reason': 'file_not_found',
            'skipped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }, ensure_ascii=False) + '\n')
        flush_batch()
        uniform = np.ones(N_DESIGNS, dtype=np.float32) / N_DESIGNS
        all_design.append(uniform)
        all_image_embs.append(np.zeros(512, dtype=np.float32))
        continue

    try:
        img = Image.open(local_path).convert('RGB')
        batch_imgs.append(img)
        batch_idxs.append(i)
    except Exception as e:
        skip_count += 1
        skip_log.write(json.dumps({
            'db_idx': int(i), 'filename': fn,
            'reason': str(e)[:200],
            'skipped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
        }, ensure_ascii=False) + '\n')
        flush_batch()
        uniform = np.ones(N_DESIGNS, dtype=np.float32) / N_DESIGNS
        all_design.append(uniform)
        all_image_embs.append(np.zeros(512, dtype=np.float32))
        continue

    if len(batch_imgs) >= GPU_BATCH_SIZE:
        flush_batch()

    done = i - start_idx + 1
    if done % 1000 == 0:
        elapsed = time.time() - t_start
        remain  = (n_total - start_idx - done) * elapsed / done
        h, m_   = divmod(int(remain), 3600)
        m_, s   = divmod(m_, 60)
        speed   = done / elapsed * 60
        print(f"   {i+1:>7,}/{n_total:,} | "
              f"경과 {elapsed/60:.1f}분 | "
              f"남은 {h}h {m_}m {s}s | "
              f"속도 {speed:.0f}장/분 | "
              f"스킵 {skip_count}개")

    if (i + 1) % SAVE_EVERY == 0:
        flush_batch()
        np.save(CLIP_DESIGN_PATH, np.array(all_design,     dtype=np.float32))
        np.save(CLIP_IMAGE_PATH,  np.array(all_image_embs, dtype=np.float32))

flush_batch()
skip_log.close()

# ==================== 저장 ====================

design_result = np.array(all_design,     dtype=np.float32)
image_result  = np.array(all_image_embs, dtype=np.float32)

np.save(CLIP_DESIGN_PATH, design_result)
np.save(CLIP_IMAGE_PATH,  image_result)

with open(CLIP_LABEL_PATH, 'w') as f:
    f.write('\n'.join(DESIGN_NAMES))

elapsed = time.time() - t_start
print(f"\n{'='*55}")
print(f"  ✅ 완료!")
print(f"     디자인  : {design_result.shape}  → {CLIP_DESIGN_PATH}")
print(f"     이미지  : {image_result.shape}   → {CLIP_IMAGE_PATH}")
print(f"     소요    : {elapsed/60:.1f}분  ({elapsed/3600:.2f}시간)")
print(f"     스킵    : {skip_count}개")
print(f"{'='*55}")
print(f"\n→ python rebuild_fused.py  로 DB 재구축하세요\n")