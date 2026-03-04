import os
import json
import cv2
import numpy as np


def embed(image: np.ndarray) -> list:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, (64, 64))
    emb = gray.flatten().astype(np.float32)
    emb /= (np.linalg.norm(emb) + 1e-6)
    return emb.tolist()


def build_index(face_dir: str, output_path: str):
    index = {}

    for fname in os.listdir(face_dir):
        if not fname.lower().endswith((".jpg", ".png", ".webp")):
            continue

        path = os.path.join(face_dir, fname)
        img = cv2.imread(path)

        if img is None:
            continue

        index[fname] = {
            "path": path,
            "embedding": embed(img)
        }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

    print(f"face index built: {len(index)} faces")


if __name__ == "__main__":
    build_index(
        face_dir="vit/preprocess/datasets/face",
        output_path="vit/preprocess/datasets/face_index.json"
    )
