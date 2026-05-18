#!/usr/bin/env python3
import cv2
import numpy as np
import pandas as pd
import os
import sys
import argparse
import multiprocessing as mp
from multiprocessing import Pool

BASE_DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
META_PATH     = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "vit", "outputs", "processed_images")
OUTPUT_PATH   = os.path.join(os.path.dirname(__file__), "color_db.npy")

DEFAULT_LAB = np.array([50.0, 0.0, 0.0, 1.0,  50.0, 0.0, 0.0, 0.0,  50.0, 0.0, 0.0, 0.0], dtype=np.float32)

_SAMPLE_CAP = 5000
_KMEANS_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 0.2)
_KMEANS_ATTEMPTS = 3


def extract_top3_lab(img_path: str):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim < 3:
        return None

    if img.shape[2] == 4:
        mask = img[:, :, 3] > 30
        bgr  = img[:, :, :3]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = gray < 240
        bgr  = img

    pixels = bgr[mask]
    if len(pixels) < 100:
        return None

    # 광택 소재 자동 감지: 상위 5% 밝기가 중앙값보다 80 이상 밝으면 하이라이트 제거
    gray_vals = (0.299 * pixels[:, 2].astype(np.float32)
                 + 0.587 * pixels[:, 1].astype(np.float32)
                 + 0.114 * pixels[:, 0].astype(np.float32))
    if float(np.percentile(gray_vals, 95)) - float(np.median(gray_vals)) > 80:
        bright_thr = float(np.percentile(gray_vals, 85))
        filtered   = pixels[gray_vals <= bright_thr]
        if len(filtered) < 50:
            filtered = pixels
    else:
        filtered = pixels

    # LAB 변환
    lab_pixels = cv2.cvtColor(
        filtered.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB
    ).reshape(-1, 3).astype(np.float32)

    # 픽셀 수 캡 (KMeans 속도 향상)
    if len(lab_pixels) > _SAMPLE_CAP:
        idx = np.random.choice(len(lab_pixels), _SAMPLE_CAP, replace=False)
        lab_pixels = lab_pixels[idx]

    n_colors = min(3, max(1, len(lab_pixels) // 100))
    _, labels, centers_lab = cv2.kmeans(
        lab_pixels, n_colors, None,
        _KMEANS_CRITERIA, _KMEANS_ATTEMPTS, cv2.KMEANS_RANDOM_CENTERS
    )
    labels = labels.flatten()
    counts = np.bincount(labels, minlength=n_colors)
    ratios = counts / counts.sum()
    order  = np.argsort(ratios)[::-1]
    centers_lab = centers_lab[order]
    ratios       = ratios[order]

    result = []
    for k in range(3):
        if k < n_colors:
            L = float(centers_lab[k][0]) * 100.0 / 255.0
            a = float(centers_lab[k][1]) - 128.0
            b = float(centers_lab[k][2]) - 128.0
            result.extend([L, a, b, float(ratios[k])])
        else:
            result.extend([50.0, 0.0, 0.0, 0.0])

    return np.array(result, dtype=np.float32)  # [12]


def _process_row(args):
    idx, product_id, major, middle, img_type = args
    lab = None
    for t in [img_type, "Model", "Product"]:
        path = os.path.join(PROCESSED_DIR, t, major, middle, f"{product_id}.webp")
        if os.path.exists(path):
            lab = extract_top3_lab(path)
            if lab is not None:
                break
    return idx, lab


def run(workers: int = None):
    if not os.path.exists(META_PATH):
        print(f"metadata.csv 없음: {META_PATH}")
        return

    metadata = pd.read_csv(META_PATH)
    total    = len(metadata)

    if workers is None:
        workers = min(mp.cpu_count(), 8)
    print(f"총 {total}개 처리 중... (workers={workers})\n")

    args_list = [
        (
            i,
            int(row["product_id"]),
            str(row.get("major_category", "")),
            str(row.get("middle_category", "")),
            str(row.get("image_type", "")),
        )
        for i, row in metadata.iterrows()
    ]

    colors  = [None] * total
    failed  = 0
    done    = 0

    with Pool(processes=workers) as pool:
        for idx, lab in pool.imap_unordered(_process_row, args_list, chunksize=50):
            colors[idx] = lab
            done += 1
            if done % 5000 == 0:
                print(f"  {done}/{total}...")

    for i in range(total):
        if colors[i] is None:
            colors[i] = DEFAULT_LAB.copy()
            failed += 1

    color_arr = np.array(colors, dtype=np.float32)
    np.save(OUTPUT_PATH, color_arr)
    print(f"\n완료! shape={color_arr.shape}, 실패={failed}")
    print(f"저장: {OUTPUT_PATH}")

    L_vals = color_arr[:, 0]
    print(f"\n명도(L) 분포: min={L_vals.min():.1f}  mean={L_vals.mean():.1f}  max={L_vals.max():.1f}")


if __name__ == "__main__":
    sys.path.insert(0, BASE_DIR)
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=None,
                        help="병렬 워커 수 (기본: CPU 코어 수, 최대 8)")
    args = parser.parse_args()
    run(workers=args.workers)
