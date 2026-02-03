"""
GCP 최적화 v4: 청크 단위 처리 + 체크포인트 복구
- 카테고리 내에서 500개씩 청크로 분할 처리 → OOM 방지
- 체크포인트: 각 청크 완료 후 results.csv 저장 → 재시작 시 복구
- 기존 처리 로직 100% 유지
"""

import torch
import pandas as pd
import requests
from PIL import Image
from io import BytesIO
from transformers import AutoImageProcessor, AutoModelForSemanticSegmentation
import numpy as np
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc

# ============================================================
# 🎯 설정
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'all_products_id.csv')
OUTPUT_BASE = '/mnt/images'
CHECKPOINT_PATH = '/mnt/images/checkpoint.csv'  # 체크포인트 파일

CHUNK_SIZE = 500        # 카테고리 내 청크 크기 (핵심 변경)
BATCH_SIZE = 32         # GPU 배치
MAX_WORKERS = 3         # 다운로드
SAVE_WORKERS = 4        # 저장
BG_REMOVE_WORKERS = 2   # 배경제거

# ============================================================
# GPU 설정
# ============================================================
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"사용 디바이스: {device}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")

# ============================================================
# 모델 로딩
# ============================================================
print("\n모델 로딩 중...")
seg_processor = AutoImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
seg_model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
seg_model = seg_model.to(device)
seg_model.eval()
print("✅ 모델 로딩 완료!\n")

# ============================================================
# 레이블 정의
# ============================================================
LABEL_NAMES = [
    'Background', 'Hat', 'Hair', 'Sunglasses', 'Upper-clothes', 
    'Skirt', 'Pants', 'Dress', 'Belt', 'Left-shoe', 
    'Right-shoe', 'Face', 'Left-leg', 'Right-leg', 'Left-arm', 
    'Right-arm', 'Bag', 'Scarf'
]
PERSON_LABELS = ['Face', 'Hair', 'Left-leg', 'Right-leg', 'Left-arm', 'Right-arm']

# ============================================================
# 기존 로직 (100% 유지)
# ============================================================

def download_image(url, timeout=30):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert('RGB')
    except:
        return None

def has_person_from_segmentation(pred_seg):
    if pred_seg is None:
        return {'has_person': None, 'person_ratio': 0, 'person_labels': {}}

    total_pixels = pred_seg.shape[0] * pred_seg.shape[1]
    person_pixels = 0
    person_label_details = {}

    for label_name in PERSON_LABELS:
        if label_name in LABEL_NAMES:
            label_idx = LABEL_NAMES.index(label_name)
            label_pixels = np.sum(pred_seg == label_idx)
            person_pixels += label_pixels
            if label_pixels > 0:
                ratio = label_pixels / total_pixels
                person_label_details[label_name] = {
                    'pixels': int(label_pixels),
                    'ratio': f"{ratio*100:.2f}%"
                }

    person_ratio = person_pixels / total_pixels
    return {
        'has_person': person_ratio >= 0.02,
        'person_ratio': person_ratio,
        'person_labels': person_label_details
    }

def remove_background_segmentation(image, pred_seg, category):
    try:
        from skimage.morphology import convex_hull_image

        CLOTH_LABELS = ['Hat', 'Upper-clothes', 'Skirt', 'Pants', 'Dress',
                       'Belt', 'Left-shoe', 'Right-shoe', 'Bag', 'Scarf']

        product_mask = np.zeros_like(pred_seg, dtype=bool)
        detected_labels = []

        for label_name in CLOTH_LABELS:
            if label_name in LABEL_NAMES:
                label_idx = LABEL_NAMES.index(label_name)
                label_mask = (pred_seg == label_idx)
                if label_mask.any():
                    product_mask |= label_mask
                    detected_labels.append(label_name)

        if not product_mask.any():
            return None, "상품 영역을 찾을 수 없음"

        product_mask = convex_hull_image(product_mask)
        img_array = np.array(image)
        alpha = np.where(product_mask, 255, 0).astype(np.uint8)
        rgba_array = np.dstack((img_array, alpha))
        result_image = Image.fromarray(rgba_array, 'RGBA')

        bbox = result_image.getbbox()
        if bbox:
            result_image = result_image.crop(bbox)

        total_pixels = product_mask.size
        product_pixels = np.sum(product_mask)
        coverage = (product_pixels / total_pixels) * 100
        process_info = f"감지: {', '.join(detected_labels)} | 커버리지: {coverage:.1f}%"

        return result_image, process_info
    except Exception as e:
        return None, f"실패: {str(e)}"

# ============================================================
# 속도 최적화 함수들 (기존 유지)
# ============================================================

def download_images_parallel(urls):
    results = [None] * len(urls)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_idx = {executor.submit(download_image, url): idx for idx, url in enumerate(urls)}
        for future in as_completed(future_to_idx):
            idx = future_to_idx[future]
            try:
                results[idx] = future.result()
            except:
                pass
    return results

def segment_images_batch(images):
    all_pred_segs = []

    for batch_idx in range(0, len(images), BATCH_SIZE):
        batch = images[batch_idx:batch_idx+BATCH_SIZE]
        valid_indices = [i for i, img in enumerate(batch) if img is not None]
        valid_images = [batch[i] for i in valid_indices]

        if not valid_images:
            all_pred_segs.extend([None] * len(batch))
            continue

        try:
            inputs = seg_processor(images=valid_images, return_tensors="pt")
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = seg_model(**inputs)

            batch_results = [None] * len(batch)
            for out_idx, orig_idx in enumerate(valid_indices):
                logits = outputs.logits[out_idx:out_idx+1]
                upsampled = torch.nn.functional.interpolate(
                    logits, size=batch[orig_idx].size[::-1],
                    mode='bilinear', align_corners=False
                )
                batch_results[orig_idx] = upsampled.argmax(dim=1)[0].cpu().numpy()

            all_pred_segs.extend(batch_results)
            del inputs, outputs, logits, upsampled
            torch.cuda.empty_cache()
        except:
            all_pred_segs.extend([None] * len(batch))

    return all_pred_segs

def remove_background_worker(args):
    idx, image, pred_seg, category = args
    if image is None or pred_seg is None:
        return idx, None, None
    result_img, info = remove_background_segmentation(image, pred_seg, category)
    return idx, result_img, info

def remove_backgrounds_parallel(images, pred_segs, category):
    tasks = []
    for idx, (img, seg) in enumerate(zip(images, pred_segs)):
        if img is not None and seg is not None:
            tasks.append((idx, img, seg, category))

    results = [None] * len(images)
    with ThreadPoolExecutor(max_workers=BG_REMOVE_WORKERS) as executor:
        futures = [executor.submit(remove_background_worker, task) for task in tasks]
        for future in as_completed(futures):
            try:
                idx, result_img, info = future.result()
                results[idx] = (result_img, info)
            except:
                pass
    return results

def save_single(args):
    filepath, image, fmt = args
    try:
        if fmt == 'PNG':
            image.save(filepath, 'PNG')
        else:
            image.save(filepath, 'JPEG', quality=85)
        return True
    except:
        return False

def save_images_parallel(save_tasks):
    with ThreadPoolExecutor(max_workers=SAVE_WORKERS) as executor:
        futures = [executor.submit(save_single, task) for task in save_tasks]
        for future in as_completed(futures):
            future.result()

# ============================================================
# 체크포인트 복구
# ============================================================

def load_checkpoint():
    """체크포인트에서 이미 처리된 ID 목록 복원"""
    if not os.path.exists(CHECKPOINT_PATH):
        return set(), []
    try:
        cp_df = pd.read_csv(CHECKPOINT_PATH)
        processed_ids = set(cp_df['id'].tolist())
        results = cp_df.to_dict('records')
        print(f"✅ 체크포인트 복원: {len(processed_ids)}개 이미 완료")
        return processed_ids, results
    except:
        return set(), []

def save_checkpoint(all_results):
    """현재까지의 결과를 체크포인트로 저장"""
    if all_results:
        pd.DataFrame(all_results).to_csv(CHECKPOINT_PATH, index=False)

# ============================================================
# 메인 처리 (청크 단위)
# ============================================================

def main():
    print("="*70)
    print("🚀 GCP 최적화 v4: 청크 단위 처리 + 체크포인트")
    print("="*70)

    # 체크포인트 복원
    processed_ids, all_results = load_checkpoint()

    # CSV 로드
    print(f"\nCSV 로딩: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH, low_memory=False)
    df.columns = ['id', 'shopping_mall', 'main_category', 'mid_category', 'category', 'brand',
                  'product_name', 'original_price', 'sale_price', 'discount_rate',
                  'product_url', 'image_url']

    print(f"✅ 전체: {len(df)}개")
    print(f"ID 범위: {df['id'].min()} ~ {df['id'].max()}")
    print(df['main_category'].value_counts())

    categories = df['main_category'].unique()
    start_time = datetime.now()
    total_processed = len(processed_ids)

    for category in categories:
        cat_df = df[df['main_category'] == category].reset_index(drop=True)

        # 이미 처리된 ID 제외
        cat_df = cat_df[~cat_df['id'].isin(processed_ids)].reset_index(drop=True)

        if len(cat_df) == 0:
            print(f"\n⏭️  {category}: 이미 완료")
            continue

        print(f"\n{'='*70}")
        print(f"📦 {category} (남은: {len(cat_df)}개)")
        print(f"{'='*70}")

        # 디렉토리 생성
        cat_dir = f"{OUTPUT_BASE}/{category}"
        os.makedirs(f"{cat_dir}/no_person/processed", exist_ok=True)
        os.makedirs(f"{cat_dir}/no_person/original", exist_ok=True)
        os.makedirs(f"{cat_dir}/with_person", exist_ok=True)

        # ─── 청크 단위 처리 ───
        for chunk_start in range(0, len(cat_df), CHUNK_SIZE):
            chunk_df = cat_df.iloc[chunk_start:chunk_start+CHUNK_SIZE].reset_index(drop=True)
            chunk_num = chunk_start // CHUNK_SIZE + 1
            total_chunks = (len(cat_df) + CHUNK_SIZE - 1) // CHUNK_SIZE

            print(f"\n  📌 청크 {chunk_num}/{total_chunks} ({len(chunk_df)}개) | "
                  f"ID: {chunk_df['id'].iloc[0]}~{chunk_df['id'].iloc[-1]}")

            # 1. 병렬 다운로드
            dl_start = datetime.now()
            images = download_images_parallel(chunk_df['image_url'].tolist())
            dl_time = (datetime.now() - dl_start).total_seconds()
            downloaded = sum(1 for i in images if i)
            print(f"    📥 다운로드: {downloaded}/{len(chunk_df)}개 ({dl_time:.1f}초)")

            # 2. GPU 배치 추론
            inf_start = datetime.now()
            pred_segs = segment_images_batch(images)
            inf_time = (datetime.now() - inf_start).total_seconds()
            print(f"    🔥 GPU 추론: {inf_time:.1f}초")

            # 3. 사람 체크
            person_checks = [has_person_from_segmentation(seg) for seg in pred_segs]

            # 4. 배경 제거
            proc_start = datetime.now()
            bg_images = [img if (pc['has_person'] == False) else None for img, pc in zip(images, person_checks)]
            bg_segs = [seg if (pc['has_person'] == False) else None for seg, pc in zip(pred_segs, person_checks)]
            processed_results = remove_backgrounds_parallel(bg_images, bg_segs, category)
            proc_time = (datetime.now() - proc_start).total_seconds()
            print(f"    🎨 배경제거: {proc_time:.1f}초")

            # 5. ID 기반 저장
            save_start = datetime.now()
            save_tasks = []
            no_person_count = 0
            with_person_count = 0

            for idx, row in chunk_df.iterrows():
                img = images[idx]
                if img is None:
                    continue

                product_id = int(row['id'])
                person_check = person_checks[idx]

                if person_check['has_person']:
                    filepath = f"{cat_dir}/with_person/{product_id}.jpg"
                    save_tasks.append((filepath, img, 'JPEG'))
                    with_person_count += 1

                    all_results.append({
                        'id': product_id,
                        'category': category,
                        'shopping_mall': row['shopping_mall'],
                        'has_person': True,
                        'preprocessed': False,
                        'saved_path': filepath,
                        'person_ratio': f"{person_check['person_ratio']*100:.1f}%"
                    })
                else:
                    orig_path = f"{cat_dir}/no_person/original/{product_id}.jpg"
                    save_tasks.append((orig_path, img, 'JPEG'))

                    bg_result = processed_results[idx]
                    if bg_result and bg_result[0] is not None:
                        proc_path = f"{cat_dir}/no_person/processed/{product_id}.png"
                        save_tasks.append((proc_path, bg_result[0], 'PNG'))
                        no_person_count += 1

                        all_results.append({
                            'id': product_id,
                            'category': category,
                            'shopping_mall': row['shopping_mall'],
                            'has_person': False,
                            'preprocessed': True,
                            'saved_path': proc_path,
                            'person_ratio': f"{person_check['person_ratio']*100:.1f}%"
                        })
                    else:
                        all_results.append({
                            'id': product_id,
                            'category': category,
                            'shopping_mall': row['shopping_mall'],
                            'has_person': False,
                            'preprocessed': False,
                            'saved_path': orig_path,
                            'person_ratio': f"{person_check['person_ratio']*100:.1f}%"
                        })

            # 병렬 저장
            save_images_parallel(save_tasks)
            save_time = (datetime.now() - save_start).total_seconds()

            total_time = dl_time + inf_time + proc_time + save_time
            print(f"    💾 저장: {save_time:.1f}초 ({len(save_tasks)}개 파일)")
            print(f"    ✅ 사람없음 {no_person_count} | 사람있음 {with_person_count} | "
                  f"⚡ {len(chunk_df)/total_time:.1f}개/초")

            # ─── 청크마다 체크포인트 저장 ───
            total_processed += len(chunk_df)
            save_checkpoint(all_results)

            # ─── 메모리 정리 ───
            del images, pred_segs, person_checks, processed_results, save_tasks, bg_images, bg_segs
            gc.collect()
            torch.cuda.empty_cache()

            # 진행률
            elapsed = (datetime.now() - start_time).total_seconds()
            speed = total_processed / elapsed if elapsed > 0 else 0
            eta = (629868 - total_processed) / speed / 3600 if speed > 0 else 0
            print(f"    📊 전체 진행: {total_processed}/629868 ({total_processed/629868*100:.1f}%) | "
                  f"속도: {speed:.1f}개/초 | ETA: {eta:.1f}시간")

    # ─── 최종 결과 CSV ───
    results_df = pd.DataFrame(all_results)
    results_df.to_csv(f'{OUTPUT_BASE}/results.csv', index=False)

    elapsed = (datetime.now() - start_time).total_seconds()
    total = len(results_df)

    print(f"\n{'='*70}")
    print(f"📊 최종 결과")
    print(f"{'='*70}")
    print(f"총 처리: {total}개")
    print(f"✅ 배경제거: {results_df['preprocessed'].sum()}개")
    print(f"❌ 사람포함: {results_df['has_person'].sum()}개")
    print(f"⏱️ 총 시간: {elapsed:.1f}초 ({elapsed/60:.1f}분)")
    print(f"⚡ 속도: {total/elapsed:.1f}개/초")

    print(f"\n{'─'*70}")
    print(f"{'카테고리':<10} {'처리':>6} {'배경제거':>8} {'사람포함':>8}")
    print(f"{'─'*70}")
    for cat in categories:
        cat_r = results_df[results_df['category'] == cat]
        print(f"{cat:<10} {len(cat_r):>6} {cat_r['preprocessed'].sum():>8} {cat_r['has_person'].sum():>8}")

if __name__ == "__main__":
    main()