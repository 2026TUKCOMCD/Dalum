import json
import numpy as np
import cv2


class FaceIndex:
    def __init__(self, index_path: str):
        with open(index_path, "r", encoding="utf-8") as f:
            self.index = json.load(f)

        if len(self.index) == 0:
            self.embeddings = None
            return

        self.embeddings = np.array(
            [v["embedding"] for v in self.index.values()],
            dtype=np.float32
        )

    def _embed(self, image: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (64, 64))
        emb = gray.flatten().astype(np.float32)
        emb /= (np.linalg.norm(emb) + 1e-6)
        return emb

    def match_all(self, crop: np.ndarray) -> list:
        """
        return: 모든 face embedding과의 cosine similarity 리스트
        """
        if self.embeddings is None:
            return []

        emb = self._embed(crop)
        sims = np.dot(self.embeddings, emb)
        return sims.tolist()
