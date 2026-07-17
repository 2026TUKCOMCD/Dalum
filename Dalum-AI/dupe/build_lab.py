#!/usr/bin/env python3
"""
공간 분할 LAB 색상 DB 구축 (KMeans 정확도 버전)

3×3 격자 × 구역별 LAB 대표색 3개 × (L,a,b,비율) = 108차원
KMeans로 정확한 대표색 추출

출력:
    embeddings_lab_spatial.npy  (N, 108)

사용법:
    python build_lab_spatial_kmeans.py
    python build_lab_spatial_kmeans.py --workers 4
"""

import numpy as np
import pandas as pd
import cv2
import os, sys, time, argparse
import boto3
from io import BytesIO
from dotenv import load_dotenv
from PIL import Image
from multiprocessing import Pool, cpu_count
from skimage.color import rgb2lab
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')  # KMeans 수렴 경고 무시
load_dotenv()

# ==================== 설정 ====================

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
AI_BASE_DIR   = os.path.dirname(BASE_DIR)
METADATA_PATH = os.path.join(AI_BASE_DIR, 'vit', 'outputs', 'vit_output', 'metadata.csv')
OUTPUT_PATH   = os.path.join(BASE_DIR, 'embeddings_lab_spatial.npy')
SAVE_EVERY    = 10000

_S3_BUCKET = os.getenv("S3_BUCKET_NAME", "dalum-storage")
_S3_PREFIX = "outputs_final/processed_images"
_s3_client = None

def _get_s3():
    global _s3_client
    if _s3_client is None:
        load_dotenv()
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
            aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )
    return _s3_client

GRID          = 3
N_COLORS      = 3
FEAT_PER_ZONE = N_COLORS * 4   # L, a, b, 비율
TOTAL_DIM     = GRID * GRID * FEAT_PER_ZONE  # 108차원
IMG_SIZE      = 64
BG_THR        = 230

parser = argparse.ArgumentParser()
parser.add_argument('--workers', type=int, default=min(cpu_count(), 4))
args = parser.parse_args()

print(f"\n{'='*55}")
print(f"  🎨 공간 분할 LAB 색상 DB 구축 (KMeans)")
print(f"{'='*55}")
print(f"  격자     : {GRID}×{GRID} = {GRID*GRID}구역")
print(f"  구역당   : LAB 대표색 {N_COLORS}개 × (L,a,b,비율)")
print(f"  총 차원  : {TOTAL_DIM}차원")
print(f"  이미지   : {IMG_SIZE}×{IMG_SIZE}")
print(f"  이미지   : {LOCAL_IMAGE_DIR}")
print(f"  CPU 코어 : {args.workers}개")
print(f"  예상시간 : 10~15시간 (4코어 기준)")
print(f"{'='*55}\n")


# ==================== 추출 함수 ====================

def extract_lab_spatial(s3_key):
    if s3_key == '__missing__':
        return np.zeros(TOTAL_DIM, dtype=np.float32)

    try:
        resp = _get_s3().get_object(Bucket=_S3_BUCKET, Key=s3_key)
        buf  = resp["Body"].read()
        arr  = np.frombuffer(buf, dtype=np.uint8)
        img  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            img = cv2.cvtColor(
                np.array(Image.open(BytesIO(buf)).convert('RGB')),
                cv2.COLOR_RGB2BGR
            )

        img_rgb = cv2.cvtColor(
            cv2.resize(img, (IMG_SIZE, IMG_SIZE)),
            cv2.COLOR_BGR2RGB
        )
        h, w   = img_rgb.shape[:2]
        zone_h = h // GRID
        zone_w = w // GRID

        feat = []
        for row in range(GRID):
            for col in range(GRID):
                zone       = img_rgb[row*zone_h:(row+1)*zone_h,
                                     col*zone_w:(col+1)*zone_w]
                pixels_rgb = zone.reshape(-1, 3).astype(np.float32) / 255.0

                # 흰색 배경 제거
                bg_mask    = np.all(pixels_rgb > BG_THR/255.0, axis=1)
                pixels_rgb = pixels_rgb[~bg_mask]

                if len(pixels_rgb) < N_COLORS:
                    feat.extend([0.0] * FEAT_PER_ZONE)
                    continue

                # RGB → LAB
                pixels_lab = rgb2lab(
                    pixels_rgb.reshape(-1, 1, 3)
                ).reshape(-1, 3)

                # KMeans 대표색
                n_c = min(N_COLORS, len(pixels_lab))
                km  = KMeans(
                    n_clusters=n_c,
                    random_state=42,
                    n_init=5,
                    max_iter=100
                ).fit(pixels_lab)

                centers = km.cluster_centers_
                counts  = np.bincount(km.labels_, minlength=n_c)
                ratios  = counts / counts.sum()

                # 비율 내림차순 정렬
                order   = np.argsort(ratios)[::-1]
                centers = centers[order]
                ratios  = ratios[order]

                zone_feat = []
                for k in range(N_COLORS):
                    if k < n_c:
                        L, a, b = centers[k]
                        zone_feat.extend([
                            float(L / 100.0),
                            float((a + 128) / 255.0),
                            float((b + 128) / 255.0),
                            float(ratios[k])
                        ])
                    else:
                        zone_feat.extend([0.0, 0.0, 0.0, 0.0])

                feat.extend(zone_feat)

        return np.array(feat, dtype=np.float32)

    except:
        return np.zeros(TOTAL_DIM, dtype=np.float32)


# ==================== 메인 ====================

if __name__ == '__main__':
    print("1️⃣  메타데이터 로드...")
    metadata = pd.read_csv(METADATA_PATH)
    n_total  = len(metadata)
    print(f"   ✅ {n_total:,}개\n")

    # 이어하기
    if os.path.exists(OUTPUT_PATH):
        existing  = np.load(OUTPUT_PATH)
        if existing.shape[1] != TOTAL_DIM:
            print(f"⚠️  차원 불일치 ({existing.shape[1]} → {TOTAL_DIM}) → 처음부터\n")
            start_idx = 0
            all_feats = []
        else:
            start_idx = len(existing)
            all_feats = list(existing)
            print(f"⏩ 이어하기: {start_idx:,}개 완료, {n_total-start_idx:,}개 남음\n")
    else:
        start_idx = 0
        all_feats = []
        print(f"🆕 처음부터: {n_total:,}개\n")

    s3_keys = []
    for i in range(start_idx, n_total):
        row = metadata.iloc[i]
        s3_key = (f"{_S3_PREFIX}/{row['image_type']}/{row['major_category']}"
                  f"/{row['middle_category']}/{int(row['product_id'])}.webp")
        s3_keys.append(s3_key)

    print(f"2️⃣  KMeans LAB 공간 분할 추출 ({args.workers}코어)...\n")
    t_start = time.time()
    CHUNK   = 1000

    with Pool(processes=args.workers) as pool:
        for batch_start in range(0, len(s3_keys), CHUNK):
            batch   = s3_keys[batch_start:batch_start + CHUNK]
            results = pool.map(extract_lab_spatial, batch)
            all_feats.extend(results)

            done       = batch_start + len(batch)
            total_done = start_idx + done
            elapsed    = time.time() - t_start
            speed      = done / elapsed * 60 if elapsed > 0 else 0
            remain     = (len(filenames) - done) / (done / elapsed) if done > 0 else 0
            h, r       = divmod(int(remain), 3600)
            m, s       = divmod(r, 60)

            print(f"   {total_done:>7,}/{n_total:,} ({total_done/n_total*100:.1f}%) | "
                  f"속도 {speed:.0f}장/분 | 남은 {h}h {m}m {s}s")

            if total_done % SAVE_EVERY < CHUNK:
                np.save(OUTPUT_PATH, np.array(all_feats, dtype=np.float32))
                print(f"   💾 중간 저장 완료 ({total_done:,}개)")

    result = np.array(all_feats, dtype=np.float32)
    np.save(OUTPUT_PATH, result)

    elapsed = time.time() - t_start
    h, r    = divmod(int(elapsed), 3600)
    m, s    = divmod(r, 60)
    print(f"\n{'='*55}")
    print(f"  ✅ 완료!")
    print(f"     shape : {result.shape}")
    print(f"     소요  : {h}h {m}m {s}s")
    print(f"     저장  : {OUTPUT_PATH}  ({os.path.getsize(OUTPUT_PATH)/1024/1024:.1f} MB)")
    print(f"{'='*55}\n")