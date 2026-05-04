#!/usr/bin/env python3
"""
color_db.npy 빌드 — 각 제품의 평균 LAB 색상 추출 (모델 불필요, 빠름)

출력: dupe/color_db.npy  shape=[N, 3]  = [L, a, b]  (CIE LAB)
  - N: metadata.csv 행 수와 정확히 일치
  - 실패 항목은 기본값 [50, 0, 0] (중간 회색) 으로 채움
"""

import cv2
import numpy as np
import pandas as pd
import os
import sys

BASE_DIR      = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
META_PATH     = os.path.join(BASE_DIR, "vit", "outputs", "vit_output", "metadata.csv")
PROCESSED_DIR = os.path.join(BASE_DIR, "vit", "outputs", "processed_images")
OUTPUT_PATH   = os.path.join(os.path.dirname(__file__), "color_db.npy")

DEFAULT_LAB = np.array([50.0, 0.0, 0.0], dtype=np.float32)


def extract_mean_lab(img_path: str):
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None or img.ndim < 3:
        return None

    if img.shape[2] == 4:
        mask = img[:, :, 3] > 30          # alpha > 30 = 의상 픽셀
        bgr  = img[:, :, :3]
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = gray < 240                  # 흰 배경 제외
        bgr  = img

    pixels = bgr[mask]
    if len(pixels) < 100:
        return None

    # 상위 15% 밝기 픽셀 제거 — 광택 소재 스페큘러 하이라이트 제거
    gray_vals = (0.299 * pixels[:, 2].astype(np.float32)
                 + 0.587 * pixels[:, 1].astype(np.float32)
                 + 0.114 * pixels[:, 0].astype(np.float32))
    bright_thr = float(np.percentile(gray_vals, 85))
    filtered   = pixels[gray_vals <= bright_thr]
    if len(filtered) < 50:
        filtered = pixels  # 픽셀 너무 적으면 원본 사용

    median_bgr     = np.median(filtered, axis=0).astype(np.float32)
    median_bgr_img = median_bgr.reshape(1, 1, 3).astype(np.uint8)
    median_lab_img = cv2.cvtColor(median_bgr_img, cv2.COLOR_BGR2LAB)

    L = float(median_lab_img[0, 0, 0]) * 100.0 / 255.0
    a = float(median_lab_img[0, 0, 1]) - 128.0
    b = float(median_lab_img[0, 0, 2]) - 128.0
    return np.array([L, a, b], dtype=np.float32)


def run():
    if not os.path.exists(META_PATH):
        print(f"metadata.csv 없음: {META_PATH}")
        return

    metadata = pd.read_csv(META_PATH)
    total    = len(metadata)
    print(f"총 {total}개 처리 중...\n")

    colors = []
    failed = 0

    for i, row in metadata.iterrows():
        product_id = int(row["product_id"])
        major      = str(row.get("major_category", ""))
        middle     = str(row.get("middle_category", ""))
        img_type   = str(row.get("image_type", ""))

        lab = None
        for t in [img_type, "Model", "Product"]:
            path = os.path.join(PROCESSED_DIR, t, major, middle, f"{product_id}.webp")
            if os.path.exists(path):
                lab = extract_mean_lab(path)
                if lab is not None:
                    break

        colors.append(lab if lab is not None else DEFAULT_LAB.copy())
        if lab is None:
            failed += 1

        if (i + 1) % 5000 == 0:
            print(f"  {i + 1}/{total}...")

    color_arr = np.array(colors, dtype=np.float32)
    np.save(OUTPUT_PATH, color_arr)
    print(f"\n완료! shape={color_arr.shape}, 실패={failed}")
    print(f"저장: {OUTPUT_PATH}")

    # 간단 통계
    L_vals = color_arr[:, 0]
    print(f"\n명도(L) 분포: min={L_vals.min():.1f}  mean={L_vals.mean():.1f}  max={L_vals.max():.1f}")


if __name__ == "__main__":
    sys.path.insert(0, BASE_DIR)
    run()
