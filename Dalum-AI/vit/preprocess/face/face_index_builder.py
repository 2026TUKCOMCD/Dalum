import os
import json
import cv2
import numpy as np


def _embed(image: np.ndarray) -> list:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64))
    hog = cv2.HOGDescriptor(
        _winSize=(64, 64),
        _blockSize=(16, 16),
        _blockStride=(8, 8),
        _cellSize=(8, 8),
        _nbins=9,
    )
    feat = hog.compute(gray).flatten().astype(np.float32)
    feat /= (np.linalg.norm(feat) + 1e-6)
    return feat.tolist()


def _load_dir(directory: str) -> dict:
    entries = {}
    if not os.path.isdir(directory):
        return entries
    for fname in os.listdir(directory):
        if not fname.lower().endswith((".jpg", ".png", ".webp")):
            continue
        path = os.path.join(directory, fname)
        img = cv2.imread(path)
        if img is None:
            continue
        entries[fname] = {"path": path, "embedding": _embed(img)}
    return entries


def build_index(face_dir: str, not_human_dir: str, output_path: str):
    positive = _load_dir(face_dir)
    negative = _load_dir(not_human_dir)

    index = {"positive": positive, "negative": negative}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"face index built: {len(positive)} positive / {len(negative)} negative")


if __name__ == "__main__":
    BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets"))
    build_index(
        face_dir=os.path.join(BASE, "face"),
        not_human_dir=os.path.join(BASE, "not_human"),
        output_path=os.path.join(BASE, "face_index.json"),
    )
