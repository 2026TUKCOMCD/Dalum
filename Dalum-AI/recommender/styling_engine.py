import logging
import math
import random
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

# 색상 페어링 점수 — 색상환 조화 이론 대신 실제 스타일링 원칙 기반.
# 원칙 1 (뉴트럴 앵커링): 강한 색 아이템의 기본 정답은 무채색 매칭.
# 원칙 2 (원 액센트): 코디에 강한 유채색은 하나만 — 유채색끼리는 톤온톤/뮤트만 안전.
ACHROMATIC_PAIR_BASE = 0.85  # 무채색끼리 — 명도 대비로 최대 +0.1
NEUTRAL_ANCHOR_SCORE = 0.9   # 유채색 + 무채색
TONAL_HUE_DIFF       = 20.0  # 같은 색 계열(톤온톤)로 보는 색상각 차이
TONAL_SCORE          = 0.85
MUTED_SATURATION     = 0.45  # 채도가 이 미만이면 뮤트 톤
MUTED_MIX_SCORE      = 0.75  # 유채색끼리라도 한쪽이 뮤트면 무난
ACCENT_CLASH_SCORE   = 0.45  # 강한 유채색 둘 — 원 액센트 룰 위반

MIN_OUTFIT_COMPAT = 0.5  # 추천 아이템 간 스타일 상호 호환 최소치

# top_k 선택 시 상위 후보 풀에서 순위 기반 기하 가중 샘플링.
# 재요청마다 조합이 달라지되 상위권일수록 뽑힐 확률이 높다.
SAMPLE_POOL_SIZE = 8
SAMPLE_DECAY     = 0.65


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
    def _hex_to_hsv(hex_color: Any) -> Optional[tuple[float, float, float]]:
        if not isinstance(hex_color, str):
            return None

        hex_color = hex_color.strip().lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(ch * 2 for ch in hex_color)
        if len(hex_color) != 6:
            return None

        try:
            r, g, b = (int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
        except ValueError:
            return None

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

    def _single_hue_harmony(
        self,
        hsv1: tuple[float, float, float],
        hsv2: tuple[float, float, float],
    ) -> float:
        h1, s1, v1 = hsv1
        h2, s2, v2 = hsv2

        achro1 = s1 < ACHROMATIC_SATURATION
        achro2 = s2 < ACHROMATIC_SATURATION

        if achro1 and achro2:
            # 무채색끼리 — 명도 대비가 클수록 소폭 가산 (0.85 ~ 0.95)
            return ACHROMATIC_PAIR_BASE + 0.1 * abs(v1 - v2)

        if achro1 or achro2:
            # 뉴트럴 앵커링 — 강한 색 + 무채색이 기본 정답
            return NEUTRAL_ANCHOR_SCORE

        diff = abs(h1 - h2) % 360
        if diff > 180:
            diff = 360 - diff

        if diff <= TONAL_HUE_DIFF:
            return TONAL_SCORE       # 톤온톤
        if min(s1, s2) < MUTED_SATURATION:
            return MUTED_MIX_SCORE   # 한쪽이 뮤트 톤이면 무난
        return ACCENT_CLASH_SCORE    # 강한 유채색 둘 — 액센트 중복

    def _prepare_colors(self, colors: Optional[List[Dict]]) -> List[tuple]:
        """
        hex 파싱에 성공한 색상만 (hsv, ratio)로 변환하고 ratio 내림차순 정렬.
        ratio가 없으면 0.0 — 정렬은 안정적이므로 원래 순서 유지.
        """
        prepared = []
        for c in colors or []:
            if not isinstance(c, dict):
                continue
            hsv = self._hex_to_hsv(c.get("hex"))
            if hsv is None:
                continue
            try:
                ratio = float(c.get("ratio", 0.0))
            except (TypeError, ValueError):
                ratio = 0.0
            prepared.append((hsv, ratio))

        prepared.sort(key=lambda x: x[1], reverse=True)
        return prepared

    def _color_harmony_score(self, colors1: Optional[List[Dict]], colors2: Optional[List[Dict]]) -> float:
        p1 = self._prepare_colors(colors1)
        p2 = self._prepare_colors(colors2)
        if not p1 or not p2:
            return 0.7

        primary = self._single_hue_harmony(p1[0][0], p2[0][0])

        # 보조색 쌍은 ratio 곱으로 가중 평균 (ratio 정보 없으면 균등 평균)
        pairs = [
            (self._single_hue_harmony(hsv_a, hsv_b), ra * rb)
            for hsv_a, ra in p1[1:]
            for hsv_b, rb in p2[1:]
        ]

        if pairs:
            total_w = sum(w for _, w in pairs)
            if total_w > 0:
                secondary = sum(s * w for s, w in pairs) / total_w
            else:
                secondary = sum(s for s, _ in pairs) / len(pairs)
            return 0.7 * primary + 0.3 * secondary
        return primary

    # ──────────────────────────────────────────
    # 스타일 호환성 점수
    # ──────────────────────────────────────────

    @staticmethod
    def _style_score(style1: Optional[str], style2: Optional[str]) -> float:
        if not style2:
            # 스타일 미상 후보는 코디 안정성을 해치므로 보수적으로 평가
            return 0.3
        if not style1:
            return 0.5
        return STYLE_COMPATIBILITY.get(style1.lower(), {}).get(style2.lower(), 0.5)

    @staticmethod
    def _styles_compatible(style1: Optional[str], style2: Optional[str]) -> bool:
        """추천 아이템끼리 같은 코디에 들어가도 어색하지 않은지 (양방향 호환)."""
        if not style1 or not style2:
            return True
        s1, s2 = style1.lower(), style2.lower()
        if s1 == s2:
            return True
        forward  = STYLE_COMPATIBILITY.get(s1, {}).get(s2, 0.5)
        backward = STYLE_COMPATIBILITY.get(s2, {}).get(s1, 0.5)
        return min(forward, backward) >= MIN_OUTFIT_COMPAT

    # ──────────────────────────────────────────
    # 최종 점수 (동적 가중치)
    # ──────────────────────────────────────────

    @staticmethod
    def _final_score(
        mat: float, col: float, sty: float,
        has_color: bool, has_style: bool,
    ) -> float:
        # 소재 유사도는 카테고리가 다른 아이템 사이에선 의미 있는 신호가 아니라서
        # (상의-신발 소재는 원래 다른 게 정상) 색상/스타일이 없을 때의 폴백으로만 쓴다.
        if has_color and has_style:
            return 0.55 * col + 0.45 * sty
        if has_color:
            return col
        if has_style:
            return sty
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

        scored: Dict[str, List[Dict]] = {}

        for cat, items in buckets.items():
            if not items:
                scored[cat] = []
                continue

            # 소재 유사도는 색상/스타일이 모두 없을 때만 최종 점수에 쓰이므로 그때만 계산
            if not has_color and not has_style:
                mat_matrix = np.array(
                    [self._to_material_vec(item.get("material_vector", [])) for item in items]
                )
                norms      = np.linalg.norm(mat_matrix, axis=1) * np.linalg.norm(input_mat_vec)
                norms      = np.where(norms == 0, 1e-10, norms)
                mat_scores = mat_matrix @ input_mat_vec / norms
            else:
                mat_scores = np.zeros(len(items))

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
                    "_style":     item.get("style"),
                })

            cat_results.sort(key=lambda x: x["score"], reverse=True)
            scored[cat] = cat_results

        return self._select_coherent(scored, top_k)

    def _sample_pick(
        self, items: List[Dict], used: set, slot_styles: List[str],
    ) -> Optional[int]:
        """
        미사용 + 슬롯 스타일 호환 후보 중 상위 SAMPLE_POOL_SIZE개에서
        순위 기반 기하 가중(SAMPLE_DECAY^rank)으로 하나를 샘플링.
        호환 후보가 없으면 점수순 차선으로 폴백해 빈 추천을 방지한다.
        """
        pool = [i for i, it in enumerate(items)
                if i not in used
                and all(self._styles_compatible(it["_style"], s) for s in slot_styles)]
        if not pool:
            pool = [i for i in range(len(items)) if i not in used]
        if not pool:
            return None

        pool    = pool[:SAMPLE_POOL_SIZE]  # items가 점수 내림차순이라 pool도 점수순
        weights = [SAMPLE_DECAY ** rank for rank in range(len(pool))]
        return random.choices(pool, weights=weights, k=1)[0]

    def _select_coherent(self, scored: Dict[str, List[Dict]], top_k: int) -> Dict[str, List[Dict]]:
        """
        슬롯(순위) 단위로 카테고리를 돌며, 같은 슬롯에 이미 뽑힌 아이템들과
        스타일이 상호 호환되는 것 중 최고점을 선택한다.
        호환 아이템이 없으면 점수순 차선으로 채워 빈 추천을 방지한다.
        """
        results: Dict[str, List[Dict]] = {cat: [] for cat in scored}
        used: Dict[str, set] = {cat: set() for cat in scored}

        for _slot in range(top_k):
            slot_styles: List[str] = []
            for cat, items in scored.items():
                pick_idx = self._sample_pick(items, used[cat], slot_styles)
                if pick_idx is None:
                    continue

                used[cat].add(pick_idx)
                it = items[pick_idx]
                if it["_style"]:
                    slot_styles.append(it["_style"])
                results[cat].append({
                    "product_id": it["product_id"],
                    "score":      it["score"],
                    "metadata":   it["metadata"],
                })

        return results
