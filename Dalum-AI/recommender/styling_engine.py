import logging
import math
from typing import Any, Dict, List, Optional

import numpy as np

from vit.preprocess.material.classes import IDX_TO_CLASS

logger = logging.getLogger(__name__)

MATERIAL_DIM = len(IDX_TO_CLASS)

CATEGORY_MAP: Dict[str, List[str]] = {
    "top":       ["bottom", "outer", "shoes", "bag", "hat"],
    "bottom":    ["top", "outer", "shoes", "bag", "hat"],
    "shoes":     ["top", "bottom", "outer"],
    "outer":     ["top" ,"bottom", "shoes", "bag"],
    "bag":       ["top", "bottom", "outer", "shoes"],
    "hat":       ["top", "bottom", "outer", "shoes"],
    "dress":     ["shoes", "bag", "hat"],
}

STYLE_COMPATIBILITY: Dict[str, Dict[str, float]] = {
    "casual":          {"casual": 1.0, "american_casual": 0.9, "street": 0.7, "vintage": 0.6, "sporty": 0.5, "formal": 0.2},
    "formal":          {"formal": 1.0, "casual": 0.3, "american_casual": 0.3, "street": 0.1, "vintage": 0.2, "sporty": 0.1},
    "sporty":          {"sporty": 1.0, "casual": 0.7, "street": 0.5, "american_casual": 0.5, "vintage": 0.3, "formal": 0.1},
    "street":          {"street": 1.0, "vintage": 0.8, "sporty": 0.7, "casual": 0.7, "american_casual": 0.2, "formal": 0.1},
    "vintage":         {"vintage": 1.0, "street": 0.8, "american_casual": 0.7, "casual": 0.6, "sporty": 0.3, "formal": 0.3},
    "american_casual": {"american_casual": 1.0, "casual": 0.8, "vintage": 0.7, "sporty": 0.5, "street": 0.2, "formal": 0.1},
}

DEFAULT_SCORE_THRESHOLD = 0.1
ACHROMATIC_SATURATION   = 0.15
OPTIONAL_THRESHOLDS: Dict[str, float] = {
    "hat": 0.5,
    "bag": 0.6,
}


class StylingRecommender:
    """
    백엔드에서 후보 상품 목록을 받아 스타일링 추천 점수를 계산하는 stateless 엔진.
    DB 연결 없음 — 모든 데이터는 요청 시 전달받음.
    """

    # ──────────────────────────────────────────
    # 소재 유사도 (코사인)
    # ──────────────────────────────────────────

    def _to_material_vec(self, material_vector: List[float]) -> np.ndarray:
        vec = np.zeros(MATERIAL_DIM, dtype=float)
        for i, v in enumerate(material_vector[:MATERIAL_DIM]):
            vec[i] = v
        return vec

    def _cosine_sim(self, v1: np.ndarray, v2: np.ndarray) -> float:
        norm = np.linalg.norm(v1) * np.linalg.norm(v2)
        return float(np.dot(v1, v2) / norm) if norm > 0 else 0.0

    # ──────────────────────────────────────────
    # 색상 조화 점수 (Hue 기반)
    # ──────────────────────────────────────────

    @staticmethod
    def _hex_to_hsv(hex_color: str) -> tuple[float, float, float]:
        hex_color = hex_color.lstrip("#")
        r, g, b   = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))

        cmax, cmin = max(r, g, b), min(r, g, b)
        delta = cmax - cmin

        s = 0.0 if cmax == 0 else delta / cmax
        v = cmax

        if delta == 0:
            h = 0.0
        elif cmax == r:
            h = 60 * (((g - b) / delta) % 6)
        elif cmax == g:
            h = 60 * ((b - r) / delta + 2)
        else:
            h = 60 * ((r - g) / delta + 4)

        return h, s, v

    def _single_hue_harmony(self, h1: float, s1: float, h2: float, s2: float) -> float:
        if s1 < ACHROMATIC_SATURATION or s2 < ACHROMATIC_SATURATION:
            return 1.0

        diff = abs(h1 - h2) % 360
        if diff > 180:
            diff = 360 - diff

        if diff <= 30:   return 1.0   # 유사색 (모노톤)
        elif diff <= 60: return 0.75  # 유사 조화
        elif diff >= 150: return 0.85  # 보색 (포인트)
        else:            return 0.4   # 부조화

    def _color_harmony_score(self, colors1: List[Dict], colors2: List[Dict]) -> float:
        if not colors1 or not colors2:
            return 0.7

        h1, s1, _ = self._hex_to_hsv(colors1[0]["hex"])
        h2, s2, _ = self._hex_to_hsv(colors2[0]["hex"])
        primary   = self._single_hue_harmony(h1, s1, h2, s2)

        secondary_scores = [
            self._single_hue_harmony(
                *self._hex_to_hsv(c1["hex"])[:2],
                *self._hex_to_hsv(c2["hex"])[:2],
            )
            for c1 in colors1[1:]
            for c2 in colors2[1:]
        ]

        if secondary_scores:
            return 0.7 * primary + 0.3 * (sum(secondary_scores) / len(secondary_scores))
        return primary

    # ──────────────────────────────────────────
    # 스타일 호환성 점수
    # ──────────────────────────────────────────

    @staticmethod
    def _style_score(style1: Optional[str], style2: Optional[str]) -> float:
        if not style1 or not style2:
            return 0.7
        return STYLE_COMPATIBILITY.get(style1.lower(), {}).get(style2.lower(), 0.5)

    # ──────────────────────────────────────────
    # 최종 점수 (동적 가중치)
    # ──────────────────────────────────────────

    @staticmethod
    def _final_score(
        mat: float, col: float, sty: float,
        has_color: bool, has_style: bool,
    ) -> float:
        if has_color and has_style:
            return 0.2 * mat + 0.3 * col + 0.50 * sty
        if has_color:
            return 0.50 * mat + 0.50 * col
        if has_style:
            return 0.50 * mat + 0.50 * sty
        return mat

    # ──────────────────────────────────────────
    # 추천 메인
    # ──────────────────────────────────────────

    def get_recommendations(
        self,
        input_material_vector: List[float],
        input_category: str,
        candidates: List[Dict[str, Any]],
        top_k: int = 3,
        input_dominant_colors: Optional[List[Dict]] = None,
        input_style: Optional[str] = None,
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
    ) -> Dict[str, List[Dict]]:
        """
        input_material_vector  : ViT 소재 확률 분포
        input_dominant_colors  : [{"hex": "#RRGGBB", "ratio": float}, ...]
        input_style            : "casual" | "formal" | "sporty" | "street" | "vintage" | "american_casual"
        candidates             : 백엔드에서 전달한 후보 상품 목록 (PostgreSQL 조회 결과)
        """
        input_mat_vec = self._to_material_vec(input_material_vector)
        has_color     = bool(input_dominant_colors)
        has_style     = bool(input_style)

        target_cats = CATEGORY_MAP.get(input_category.lower())
        if target_cats is None:
            logger.warning(f"알 수 없는 카테고리: '{input_category}'")
            target_cats = list(CATEGORY_MAP.keys())

        # 카테고리별로 후보 분류
        buckets: Dict[str, List[Dict]] = {cat: [] for cat in target_cats}
        for item in candidates:
            cat = item.get("category", "").lower()
            if cat in buckets:
                buckets[cat].append(item)

        results: Dict[str, List[Dict]] = {}

        for cat, items in buckets.items():
            if not items:
                results[cat] = []
                continue

            # 소재 행렬 일괄 변환 후 배치 코사인 유사도
            mat_matrix = np.array(
                [self._to_material_vec(item.get("material_vector", [])) for item in items]
            )
            norms      = np.linalg.norm(mat_matrix, axis=1) * np.linalg.norm(input_mat_vec)
            norms      = np.where(norms == 0, 1e-10, norms)
            mat_scores = mat_matrix @ input_mat_vec / norms

            cat_results = []
            for i, item in enumerate(items):
                col_score = (
                    self._color_harmony_score(input_dominant_colors, item.get("dominant_colors", []))
                    if has_color else 0.0
                )
                sty_score = self._style_score(input_style, item.get("style"))
                score     = self._final_score(float(mat_scores[i]), col_score, sty_score, has_color, has_style)

                if score < OPTIONAL_THRESHOLDS.get(cat, score_threshold):
                    continue

                cat_results.append({
                    "product_id": item.get("id"),
                    "score":      round(score, 4),
                    "metadata":   item.get("metadata", {}),
                })

            cat_results.sort(key=lambda x: x["score"], reverse=True)
            results[cat] = cat_results[:top_k]

        return results
