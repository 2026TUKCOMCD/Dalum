#!/usr/bin/env python3
"""
ViT 다중 레이어 임베딩 배치 추출 (GCS 멀티프로세싱 버전)

GCS 경로: gs://dalum/processed/processed/{id}.png
saved_path: /mnt/images/OUTER/no_person/processed/1.png → 파일명만 추출

출력:
    embeddings_color.npy   - layer 3  [N, 768]
    embeddings_texture.npy - layer 7  [N, 768]
    embeddings_shape.npy   - layer 11 [N, 768]

사용법:
    python extract_multilayer_embeddings.py
"""

import torch
import numpy as np
import pandas as pd
from transformers import ViTModel, ViTImageProcessor
from PIL import Image
from google.cloud import storage
import io
import os
import time
import queue
import threading
from tqdm import tqdm

# ==================== 설정 ====================

METADATA_PATH  = 'embeddings_metadata.csv'
OUTPUT_COLOR   = 'embeddings_color.npy'
OUTPUT_TEXTURE = 'embeddings_texture.npy'
OUTPUT_SHAPE   = 'embeddings_shape.npy'
CKPT_PATH      = 'extract_checkpoint.npy'

GCS_BUCKET     = 'dalum'
GCS_PREFIX     = 'processed/processed/'   # 버킷 실제 경로

BATCH_SIZE     = 64     # GPU 배치 크기 (에러나면 32로 줄이세요)
NUM_WORKERS    = 16     # GCS 다운로드 스레드 수
QUEUE_SIZE     = 256    # 프리페치 큐 크기
SAVE_EVERY     = 5000
DEVICE         = 'cuda' if torch.cuda.is_available() else 'cpu'

# ==================== 모델 로드 ====================

print("🚀 ViT 다중 레이어 임베딩 배치 추출 (멀티스레드 GCS)\n")
print(f"   디바이스: {DEVICE}")
print(f"   버킷: gs://{GCS_BUCKET}/{GCS_PREFIX}")
print(f"   다운로드 스레드: {NUM_WORKERS}개\n")

print("1️⃣  ViT 모델 로드...")
vit_model     = ViTModel.from_pretrained("google/vit-base-patch16-224")
vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
vit_model     = vit_model.to(DEVICE)
vit_model.eval()
print("   ✅ 완료\n")

# ==================== 메타데이터 ====================

print("2️⃣  메타데이터 로드...")
metadata = pd.read_csv(METADATA_PATH)
n_total  = len(metadata)
print(f"   ✅ 총 {n_total:,}개 상품\n")

# ==================== 체크포인트 ====================

if os.path.exists(CKPT_PATH):
    ckpt         = np.load(CKPT_PATH, allow_pickle=True).item()
    start_idx    = ckpt['next_idx']
    color_list   = list(ckpt['color'])
    texture_list = list(ckpt['texture'])
    shape_list   = list(ckpt['shape'])
    failed_list  = list(ckpt.get('failed', []))
    print(f"⏩ 체크포인트 발견 → {start_idx:,}번부터 이어서 시작\n")
else:
    start_idx    = 0
    color_list   = []
    texture_list = []
    shape_list   = []
    failed_list  = []
    print("🆕 처음부터 시작\n")

# ==================== GCS 멀티스레드 프리페처 ====================

class GCSPrefetcher:
    """
    백그라운드 스레드 NUM_WORKERS개로 GCS에서 이미지를 미리 다운받아
    큐에 쌓아두는 프리페처.
    GPU가 추론하는 동안 다음 배치를 미리 준비해서 I/O 병목을 줄임.
    """
    def __init__(self, paths, num_workers=16, queue_size=256):
        self.paths      = paths
        self.queue      = queue.Queue(maxsize=queue_size)
        self.num_workers = num_workers
        self._stop      = threading.Event()

        # GCS 클라이언트는 스레드마다 별도 생성 (thread-safe)
        self.threads = []
        chunk_size   = (len(paths) + num_workers - 1) // num_workers

        for t_id in range(num_workers):
            chunk = paths[t_id * chunk_size : (t_id + 1) * chunk_size]
            if not chunk:
                continue
            t = threading.Thread(
                target=self._worker,
                args=(chunk, t_id),
                daemon=True
            )
            t.start()
            self.threads.append(t)

    def _worker(self, paths_chunk, t_id):
        client = storage.Client()
        bucket = client.bucket(GCS_BUCKET)

        for idx, (orig_idx, saved_path) in enumerate(paths_chunk):
            if self._stop.is_set():
                break
            try:
                filename  = os.path.basename(saved_path)   # '1.png'
                gcs_path  = GCS_PREFIX + filename           # 'processed/processed/1.png'
                blob      = bucket.blob(gcs_path)
                img_bytes = blob.download_as_bytes()
                img       = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                self.queue.put((orig_idx, img))
            except Exception:
                self.queue.put((orig_idx, None))   # 실패도 None으로 넣어서 순서 유지

    def __iter__(self):
        total    = len(self.paths)
        received = 0
        while received < total:
            item = self.queue.get()
            yield item
            received += 1

    def stop(self):
        self._stop.set()


# ==================== 배치 추론 ====================

def process_batch(batch):
    """
    batch: [(orig_idx, img), ...]
    반환: (orig_indices, c_arr, t_arr, s_arr, failed_indices)
    """
    orig_indices = [b[0] for b in batch]
    images       = [b[1] for b in batch]
    valid_imgs   = [img for img in images if img is not None]
    valid_mask   = [img is not None for img in images]
    failed       = [orig_indices[k] for k, v in enumerate(valid_mask) if not v]

    n = len(batch)
    c_arr = np.zeros((n, 768), dtype=np.float32)
    t_arr = np.zeros((n, 768), dtype=np.float32)
    s_arr = np.zeros((n, 768), dtype=np.float32)

    if not valid_imgs:
        return orig_indices, c_arr, t_arr, s_arr, failed

    inputs = vit_processor(images=valid_imgs, return_tensors="pt")
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = vit_model(**inputs, output_hidden_states=True)
        hidden  = outputs.hidden_states
        c_v = hidden[3][:, 0, :].cpu().numpy()    # 색상  [valid_n, 768]
        t_v = hidden[7][:, 0, :].cpu().numpy()    # 텍스처
        s_v = hidden[11][:, 0, :].cpu().numpy()   # 형태

    v = 0
    for k, is_valid in enumerate(valid_mask):
        if is_valid:
            c_arr[k] = c_v[v]
            t_arr[k] = t_v[v]
            s_arr[k] = s_v[v]
            v += 1

    return orig_indices, c_arr, t_arr, s_arr, failed


# ==================== 메인 추출 루프 ====================

print("3️⃣  배치 추출 시작...")
print(f"   배치 크기: {BATCH_SIZE} / 스레드: {NUM_WORKERS} / 큐: {QUEUE_SIZE}\n")

# 처리할 (원본 인덱스, saved_path) 리스트
remaining_paths = [
    (i, metadata.iloc[i]['saved_path'])
    for i in range(start_idx, n_total)
]

# 결과를 인덱스 순서대로 보관하기 위한 임시 딕셔너리
# (멀티스레드라 순서가 뒤섞일 수 있음 → 나중에 정렬)
result_dict = {}

prefetcher = GCSPrefetcher(remaining_paths, NUM_WORKERS, QUEUE_SIZE)

t_start  = time.time()
batch    = []
pbar     = tqdm(total=len(remaining_paths), desc="추출 중", unit="개")

for orig_idx, img in prefetcher:
    batch.append((orig_idx, img))

    is_last = (len(result_dict) + len(batch) == len(remaining_paths))

    if len(batch) == BATCH_SIZE or is_last:
        orig_indices, c_arr, t_arr, s_arr, failed = process_batch(batch)

        for k, idx in enumerate(orig_indices):
            result_dict[idx] = (c_arr[k], t_arr[k], s_arr[k])
        failed_list.extend(failed)

        pbar.update(len(batch))
        batch = []

        # 진행률
        done    = start_idx + len(result_dict)
        elapsed = time.time() - t_start
        speed   = len(result_dict) / elapsed if elapsed > 0 else 1
        eta     = (n_total - done) / speed / 3600
        pbar.set_postfix({
            '완료': f'{done:,}',
            'ETA' : f'{eta:.1f}h',
            '실패': len(failed_list),
            '속도': f'{speed:.0f}/s'
        })

        # 중간 저장 (체크포인트는 순서대로 저장)
        if len(result_dict) % SAVE_EVERY < BATCH_SIZE or is_last:
            # 지금까지 모인 결과를 인덱스 순으로 정렬해서 리스트에 추가
            sorted_keys = sorted(result_dict.keys())
            c_tmp = [result_dict[k][0] for k in sorted_keys]
            t_tmp = [result_dict[k][1] for k in sorted_keys]
            s_tmp = [result_dict[k][2] for k in sorted_keys]

            # 기존 체크포인트 리스트 + 이번 결과 합치기
            all_c = color_list   + c_tmp
            all_t = texture_list + t_tmp
            all_s = shape_list   + s_tmp

            np.save(CKPT_PATH, {
                'next_idx': start_idx + len(result_dict),
                'color'   : np.array(all_c, dtype=np.float32),
                'texture' : np.array(all_t, dtype=np.float32),
                'shape'   : np.array(all_s, dtype=np.float32),
                'failed'  : failed_list
            })

pbar.close()
prefetcher.stop()

# ==================== 최종 저장 ====================

print("\n4️⃣  최종 저장 중...")

sorted_keys  = sorted(result_dict.keys())
color_list   = color_list   + [result_dict[k][0] for k in sorted_keys]
texture_list = texture_list + [result_dict[k][1] for k in sorted_keys]
shape_list   = shape_list   + [result_dict[k][2] for k in sorted_keys]

color_arr   = np.array(color_list,   dtype=np.float32)
texture_arr = np.array(texture_list, dtype=np.float32)
shape_arr   = np.array(shape_list,   dtype=np.float32)

np.save(OUTPUT_COLOR,   color_arr)
np.save(OUTPUT_TEXTURE, texture_arr)
np.save(OUTPUT_SHAPE,   shape_arr)

if os.path.exists(CKPT_PATH):
    os.remove(CKPT_PATH)

elapsed_total = (time.time() - t_start) / 3600

print(f"\n✅ 완료!")
print(f"   color   : {OUTPUT_COLOR}   {color_arr.shape}")
print(f"   texture : {OUTPUT_TEXTURE} {texture_arr.shape}")
print(f"   shape   : {OUTPUT_SHAPE}   {shape_arr.shape}")
print(f"   실패    : {len(failed_list)}개 (zeros로 대체됨)")
print(f"   총 소요 : {elapsed_total:.1f}시간")
print(f"\n✅ 다음 단계: python recommend_attention.py --build")

if failed_list:
    pd.DataFrame({'failed_idx': failed_list}).to_csv('extract_failed.csv', index=False)
    print(f"   실패 목록: extract_failed.csv 저장됨")
