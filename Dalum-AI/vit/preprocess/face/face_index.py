import json
import numpy as np
import cv2


class FaceIndex:
    def __init__(self, index_path: str):
        with open(index_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        # 신규 포맷(positive/negative) vs 구버전(flat dict) 호환
        if "positive" in raw:
            pos_data = raw["positive"]
            neg_data = raw.get("negative", {})
        else:
            pos_data = raw
            neg_data = {}

        self.pos_embeddings = self._load_array(pos_data)
        self.neg_embeddings = self._load_array(neg_data)

    def _load_array(self, data: dict) -> np.ndarray | None:
        if not data:
            return None
        return np.array([v["embedding"] for v in data.values()], dtype=np.float32)

    def _embed(self, image: np.ndarray) -> np.ndarray:
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
        return feat

    def score(self, crop: np.ndarray) -> float:
        if self.pos_embeddings is None:
            return 0.0

        emb = self._embed(crop)
        pos_sim = float(np.max(np.dot(self.pos_embeddings, emb)))

        if self.neg_embeddings is not None:
            neg_sim = float(np.max(np.dot(self.neg_embeddings, emb)))
            return pos_sim - neg_sim

        return pos_sim

    def match_all(self, crop: np.ndarray) -> list:
        """하위 호환용"""
        if self.pos_embeddings is None:
            return []
        emb = self._embed(crop)
        return np.dot(self.pos_embeddings, emb).tolist()
