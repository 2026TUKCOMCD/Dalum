import os
import cv2
import numpy as np
import pandas as pd
import faiss
import torch
import torch.nn.functional as F
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
from sklearn.cluster import KMeans

# 카테고리별 가중치 설정
_CATEGORY_WEIGHTS = {
    "TOP": {
        "default":   dict(clip_image=0.12, vit_color=0.03, shape=0.10, material=0.08, clip_design=0.25, clip_color=0.15, lab=0.27),
        "chromatic": dict(clip_image=0.10, vit_color=0.02, shape=0.10, material=0.01, clip_design=0.12, clip_color=0.20, lab=0.45),
        "material":  dict(clip_image=0.25, vit_color=0.02, shape=0.25, material=0.15, clip_design=0.20, clip_color=0.08, lab=0.05),
    },
    "OUTER": {
        "default":   dict(clip_image=0.22, vit_color=0.02, shape=0.22, material=0.18, clip_design=0.15, clip_color=0.10, lab=0.11),
        "chromatic": dict(clip_image=0.15, vit_color=0.02, shape=0.20, material=0.03, clip_design=0.08, clip_color=0.18, lab=0.34),
        "material":  dict(clip_image=0.22, vit_color=0.02, shape=0.35, material=0.12, clip_design=0.18, clip_color=0.05, lab=0.06),
    },
    "BOTTOM": {
        "default":   dict(clip_image=0.20, vit_color=0.03, shape=0.28, material=0.15, clip_design=0.15, clip_color=0.10, lab=0.09),
        "chromatic": dict(clip_image=0.10, vit_color=0.02, shape=0.15, material=0.05, clip_design=0.10, clip_color=0.18, lab=0.40),
        "material":  dict(clip_image=0.25, vit_color=0.02, shape=0.30, material=0.10, clip_design=0.15, clip_color=0.12, lab=0.06),
    },
    "DRESS": {
        "default":   dict(clip_image=0.20, vit_color=0.02, shape=0.20, material=0.05, clip_design=0.25, clip_color=0.13, lab=0.15),
        "chromatic": dict(clip_image=0.10, vit_color=0.02, shape=0.10, material=0.02, clip_design=0.12, clip_color=0.20, lab=0.44),
        "material":  dict(clip_image=0.25, vit_color=0.02, shape=0.25, material=0.15, clip_design=0.20, clip_color=0.08, lab=0.05),
    },
    "BAG": {
        "default":   dict(clip_image=0.30, vit_color=0.02, shape=0.25, material=0.20, clip_design=0.10, clip_color=0.08, lab=0.05),
        "chromatic": dict(clip_image=0.15, vit_color=0.02, shape=0.15, material=0.10, clip_design=0.08, clip_color=0.18, lab=0.32),
        "material":  dict(clip_image=0.35, vit_color=0.02, shape=0.30, material=0.15, clip_design=0.10, clip_color=0.05, lab=0.03),
    },
    "SHOES": {
        "default":   dict(clip_image=0.30, vit_color=0.02, shape=0.28, material=0.15, clip_design=0.10, clip_color=0.10, lab=0.05),
        "chromatic": dict(clip_image=0.15, vit_color=0.02, shape=0.18, material=0.08, clip_design=0.08, clip_color=0.18, lab=0.31),
        "material":  dict(clip_image=0.35, vit_color=0.02, shape=0.32, material=0.12, clip_design=0.10, clip_color=0.05, lab=0.04),
    },
    "HAT": {
        "default":   dict(clip_image=0.25, vit_color=0.03, shape=0.20, material=0.10, clip_design=0.20, clip_color=0.12, lab=0.10),
        "chromatic": dict(clip_image=0.12, vit_color=0.02, shape=0.12, material=0.05, clip_design=0.12, clip_color=0.18, lab=0.39),
        "material":  dict(clip_image=0.28, vit_color=0.02, shape=0.25, material=0.15, clip_design=0.15, clip_color=0.10, lab=0.05),
    },
}
_FALLBACK_WEIGHTS = {
    "default":   dict(clip_image=0.12, vit_color=0.02, shape=0.15, material=0.12, clip_design=0.22, clip_color=0.12, lab=0.25),
    "chromatic": dict(clip_image=0.10, vit_color=0.02, shape=0.10, material=0.01, clip_design=0.12, clip_color=0.20, lab=0.45),
    "material":  dict(clip_image=0.35, vit_color=0.02, shape=0.35, material=0.10, clip_design=0.15, clip_color=0.02, lab=0.01),
}

MMR_THRESHOLD        = 0.97
SELF_MATCH_THRESHOLD = 0.99  # faiss 이 값 이상이면 동일 제품으로 간주해 제외

# 경로 설정

_BASE    = os.path.dirname(os.path.abspath(__file__))
_AI_BASE = os.path.dirname(_BASE)

CLIP_IMAGE_PATH  = os.path.join(_BASE, "embeddings_clip_image.npy")
CLIP_DESIGN_PATH = os.path.join(_BASE, "embeddings_clip_design.npy")
DALUM_VIT_PATH   = os.path.join(_AI_BASE, "vit", "outputs", "vit_output", "embeddings.npy")
META_PATH        = os.path.join(_AI_BASE, "vit", "outputs", "vit_output", "metadata.csv")
COLOR_DB_PATH    = os.path.join(_BASE, "color_db.npy")  # 평균 LAB [N, 3]

from dupe.prompts import COLOR_PROMPTS, DESIGN_NAMES, DESIGN_TEXTS

# 디자인 그룹 분류
_PLAIN_DESIGN_NAMES = {"solid", "gradient"}
_MATERIAL_DESIGN_NAMES = {
    "leather", "nylon", "denim", "knit", "fur", "fleece", "wool", "quilted",
    "velvet", "silk_satin", "linen", "sheer", "washed", "lace",
}
_SHAPE_DESIGN_NAMES = {
    "oversized", "slim_fitted", "cropped", "longline", "mini_length",
    "hooded", "high_neck", "lapel_collar", "collarless", "off_shoulder",
    "double_breasted", "belted", "zip_front", "half_zip", "open_front",
    "bomber_silhouette", "moto_biker",
    "wide_leg_bottom", "slim_leg_bottom", "flared_bottom",
    "varsity",
}
_PATTERN_DESIGN_NAMES = (
    set(DESIGN_NAMES) - _PLAIN_DESIGN_NAMES - _MATERIAL_DESIGN_NAMES - _SHAPE_DESIGN_NAMES
)
_PATTERN_DESIGN_INDICES = [i for i, n in enumerate(DESIGN_NAMES) if n in _PATTERN_DESIGN_NAMES]

# CLIP 소재 디자인명 → DB small_category 키워드 매핑 (소분류 인덱스 검색용)
_DESIGN_TO_SMALL_HINT: dict[str, list[str]] = {
    "leather"   : ["가죽"],
    "denim"     : ["데님"],
    "knit"      : ["니트"],
    "fur"       : ["퍼", "무스탕"],
    "nylon"     : ["나일론", "코치"],
    "fleece"    : ["플리스"],
    "wool"      : ["울", "캐시미어"],
    "velvet"    : ["벨벳"],
    "quilted"   : ["패딩"],
    "silk_satin": ["실크", "새틴"],
    "linen"     : ["린넨"],
    "sheer"     : ["쉬폰", "시스루"],
    "lace"      : ["레이스"],
}

# 카테고리 감지 프롬프트

from dupe.prompts import (
    CATEGORY_NAMES, CATEGORY_TEXTS,
    MIDDLE_CATEGORY_PROMPTS,
    SMALL_CATEGORY_PROMPTS,
)

# 초기화

print("듀프 추천 시스템 초기화...\n")
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"   디바이스: {device}")

print("CLIP 모델 로드...")
clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(device)
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()

with torch.no_grad():
    _text_inputs  = clip_processor(text=DESIGN_TEXTS, return_tensors="pt", padding=True).to(device)
    _text_out     = clip_model.get_text_features(**_text_inputs)
    if not isinstance(_text_out, torch.Tensor):
        _text_out = _text_out.pooler_output
    _cached_text_embs = F.normalize(_text_out, dim=-1)

    _cat_inputs  = clip_processor(text=CATEGORY_TEXTS, return_tensors="pt", padding=True).to(device)
    _cat_out     = clip_model.get_text_features(**_cat_inputs)
    if not isinstance(_cat_out, torch.Tensor):
        _cat_out = _cat_out.pooler_output
    _cached_cat_embs = F.normalize(_cat_out, dim=-1)

    _cached_middle_embs = {}
    for _major, _mid_dict in MIDDLE_CATEGORY_PROMPTS.items():
        _mid_texts = list(_mid_dict.values())
        _mid_names = list(_mid_dict.keys())
        _mid_inputs = clip_processor(text=_mid_texts, return_tensors="pt", padding=True).to(device)
        _mid_out = clip_model.get_text_features(**_mid_inputs)
        if not isinstance(_mid_out, torch.Tensor):
            _mid_out = _mid_out.pooler_output
        _cached_middle_embs[_major] = (_mid_names, F.normalize(_mid_out, dim=-1))

    _cached_small_embs = {}
    for (_major, _mid), _small_dict in SMALL_CATEGORY_PROMPTS.items():
        if len(_small_dict) <= 1:
            continue  # 소분류가 1개뿐이면 감지 불필요
        _small_texts = list(_small_dict.values())
        _small_names = list(_small_dict.keys())
        _small_inputs = clip_processor(text=_small_texts, return_tensors="pt", padding=True).to(device)
        _small_out = clip_model.get_text_features(**_small_inputs)
        if not isinstance(_small_out, torch.Tensor):
            _small_out = _small_out.pooler_output
        _cached_small_embs[(_major, _mid)] = (_small_names, F.normalize(_small_out, dim=-1))

    _color_inputs = clip_processor(text=COLOR_PROMPTS, return_tensors="pt", padding=True).to(device)
    _color_out    = clip_model.get_text_features(**_color_inputs)
    if not isinstance(_color_out, torch.Tensor):
        _color_out = _color_out.pooler_output
    _cached_color_text_embs = F.normalize(_color_out, dim=-1)  # [C, 512]
print("   완료")

# ViT lazy 로드 (recommend() 직접 호출 시 shape 임베딩 추출용)
_vit_model     = None
_vit_processor = None

def _get_vit():
    global _vit_model, _vit_processor
    if _vit_model is None:
        from transformers import ViTModel, ViTImageProcessor
        _vit_model = ViTModel.from_pretrained(
            "google/vit-base-patch16-224", local_files_only=True
        ).to(device)
        _vit_model.eval()
        _vit_processor = ViTImageProcessor.from_pretrained(
            "google/vit-base-patch16-224", local_files_only=True
        )
    return _vit_model, _vit_processor

print("임베딩 DB 로드...")
_missing = [p for p in [CLIP_IMAGE_PATH, CLIP_DESIGN_PATH, DALUM_VIT_PATH, META_PATH]
            if not os.path.exists(p)]

if _missing:
    print(f"   ⚠️  아래 파일이 없어 듀프 검색을 사용할 수 없습니다:")
    for p in _missing:
        print(f"      - {p}")
    clip_image_db        = None
    clip_design_db       = None
    dalum_vit_db         = None
    metadata             = None
    faiss_indices        = None
    faiss_middle_indices = None
    faiss_index_all      = None
    _db_color_probs      = None
    mean_lab_db          = None
else:
    clip_image_db  = np.load(CLIP_IMAGE_PATH)
    _clip_design_raw = np.load(CLIP_DESIGN_PATH)
    dalum_vit_db   = np.load(DALUM_VIT_PATH)
    metadata       = pd.read_csv(META_PATH)

    # 디자인 DB 크기 호환성 체크 (프롬프트 변경 후 재빌드 전 인덱스 불일치 방지)
    _expected_design_size = len(DESIGN_NAMES)
    if _clip_design_raw.shape[1] != _expected_design_size:
        print(f"   ⚠️  CLIP 디자인 DB 크기 불일치: DB={_clip_design_raw.shape[1]}차원, "
              f"현재 프롬프트={_expected_design_size}차원")
        print(f"      → python -m dupe.build_clip 재빌드 필요! (디자인 게이트 임시 비활성화)")
        clip_design_db = None
    else:
        clip_design_db = _clip_design_raw

    # 카테고리별 FAISS 인덱스 구축
    faiss_indices = {}
    _all_categories = metadata["major_category"].unique()

    for _cat in _all_categories:
        _mask     = (metadata["major_category"] == _cat).values
        _db_idxs  = np.where(_mask)[0]
        _vecs     = clip_image_db[_db_idxs].astype("float32").copy()
        faiss.normalize_L2(_vecs)
        _idx = faiss.IndexFlatIP(512)
        _idx.add(_vecs)
        faiss_indices[str(_cat)] = (_idx, _db_idxs)

    # 중분류별 FAISS 인덱스 구축
    faiss_middle_indices = {}
    for _cat in _all_categories:
        _major_mask = (metadata["major_category"] == _cat).values
        _middle_cats = metadata[_major_mask]["middle_category"].dropna().unique()
        for _mid in _middle_cats:
            if str(_mid) == "" or str(_mid) == "nan":
                continue
            _mid_mask = _major_mask & (metadata["middle_category"] == _mid).values
            _db_idxs  = np.where(_mid_mask)[0]
            if len(_db_idxs) < 10:
                continue
            _vecs = clip_image_db[_db_idxs].astype("float32").copy()
            faiss.normalize_L2(_vecs)
            _idx = faiss.IndexFlatIP(512)
            _idx.add(_vecs)
            faiss_middle_indices[(str(_cat), str(_mid))] = (_idx, _db_idxs)

    # 소분류별 FAISS 인덱스 구축 (small_category 컬럼 있을 때만)
    faiss_small_indices = {}
    if "small_category" in metadata.columns:
        for _cat in _all_categories:
            _major_mask = (metadata["major_category"] == _cat).values
            _middle_cats = metadata[_major_mask]["middle_category"].dropna().unique()
            for _mid in _middle_cats:
                if str(_mid) in ("", "nan"):
                    continue
                _mid_mask = _major_mask & (metadata["middle_category"] == _mid).values
                _small_cats = metadata[_mid_mask]["small_category"].dropna().unique()
                for _small in _small_cats:
                    if str(_small) in ("", "nan"):
                        continue
                    _small_mask = _mid_mask & (metadata["small_category"] == _small).values
                    _db_idxs    = np.where(_small_mask)[0]
                    if len(_db_idxs) < 5:
                        continue
                    _vecs = clip_image_db[_db_idxs].astype("float32").copy()
                    faiss.normalize_L2(_vecs)
                    _idx = faiss.IndexFlatIP(512)
                    _idx.add(_vecs)
                    faiss_small_indices[(str(_cat), str(_mid), str(_small))] = (_idx, _db_idxs)
        print(f"   소분류 인덱스: {len(faiss_small_indices)}개")
    else:
        print("   소분류 인덱스: small_category 없음 (run_add_small_category.py 실행 필요)")

    # 전체 검색용 fallback 인덱스
    _clip_norm = clip_image_db.copy().astype("float32")
    faiss.normalize_L2(_clip_norm)
    faiss_index_all = faiss.IndexFlatIP(512)
    faiss_index_all.add(_clip_norm)

    # DB 전체에 대한 색상 분포 사전 계산
    print("   CLIP 색상 분포 계산 중...")
    _clip_image_tensor = torch.tensor(clip_image_db, dtype=torch.float32).to(device)
    with torch.no_grad():
        _db_color_logits = (_clip_image_tensor @ _cached_color_text_embs.T) * 100
        _db_color_probs  = F.softmax(_db_color_logits, dim=-1).cpu().numpy().astype("float32")
    del _clip_image_tensor

    # LAB 색상 DB 로드 ([N,12] top3 또는 [N,3] 레거시)
    if os.path.exists(COLOR_DB_PATH):
        _color_raw = np.load(COLOR_DB_PATH)
        if _color_raw.ndim == 2 and _color_raw.shape[1] == 12:
            # top3 포맷: ratio 가중 평균으로 [N, 3] 변환
            _top3 = _color_raw.reshape(-1, 3, 4)
            mean_lab_db = np.sum(_top3[:, :, :3] * _top3[:, :, 3:4], axis=1).astype(np.float32)
        else:
            mean_lab_db = _color_raw
        print(f"   LAB 색상 DB: {_color_raw.shape} → {mean_lab_db.shape}")
    else:
        mean_lab_db = None
        print("   LAB 색상 DB 없음 → python -m dupe.build_color_db 실행 필요")

    print(f"   CLIP 이미지:  {clip_image_db.shape}")
    print(f"   CLIP 디자인:  {clip_design_db.shape if clip_design_db is not None else '비활성화 (재빌드 필요)'}")
    print(f"   Dalum ViT:   {dalum_vit_db.shape}")
    print(f"   CLIP 색상분포: {_db_color_probs.shape}")
    print(f"   메타데이터:   {len(metadata)}개")
    print(f"   대분류 인덱스: {list(faiss_indices.keys())}")
    print(f"   중분류 인덱스: {len(faiss_middle_indices)}개")
    print(f"   소분류 인덱스: {len(faiss_small_indices)}개")

print("초기화 완료!\n")


# 쿼리 특징 추출

def extract_clip_features(image_pil):
    """CLIP 이미지 임베딩 + 디자인 점수 추출"""
    clip_input = clip_processor(images=image_pil, return_tensors="pt").to(device)
    with torch.no_grad():
        img_feats = clip_model.get_image_features(**clip_input)
        if not isinstance(img_feats, torch.Tensor):
            img_feats = img_feats.pooler_output
        img_emb      = F.normalize(img_feats, dim=-1)
        logits       = (img_emb @ _cached_text_embs.T) * 100
        design_probs = F.softmax(logits, dim=-1)[0].cpu().numpy()

    design_scores = {name: float(p) for name, p in zip(DESIGN_NAMES, design_probs)}
    return img_emb.cpu().numpy().astype("float32"), design_scores, design_probs


def detect_major_category(image_pil=None, clip_emb: np.ndarray = None) -> str:
    if clip_emb is not None:
        img_emb = torch.tensor(clip_emb, dtype=torch.float32).to(device)
        if img_emb.dim() == 1:
            img_emb = img_emb.unsqueeze(0)
        img_emb = F.normalize(img_emb, dim=-1)
    else:
        clip_input = clip_processor(images=image_pil, return_tensors="pt").to(device)
        with torch.no_grad():
            img_feats = clip_model.get_image_features(**clip_input)
            if not isinstance(img_feats, torch.Tensor):
                img_feats = img_feats.pooler_output
            img_emb = F.normalize(img_feats, dim=-1)

    with torch.no_grad():
        logits = (img_emb @ _cached_cat_embs.T) * 100
        probs  = F.softmax(logits, dim=-1)[0].cpu().numpy()

    best_idx = int(probs.argmax())
    return CATEGORY_NAMES[best_idx]


def detect_middle_category(clip_emb: np.ndarray, major_category: str) -> str:
    if major_category not in _cached_middle_embs:
        return ""

    mid_names, text_embs = _cached_middle_embs[major_category]

    img_emb = torch.tensor(clip_emb, dtype=torch.float32).to(device)
    if img_emb.dim() == 1:
        img_emb = img_emb.unsqueeze(0)
    img_emb = F.normalize(img_emb, dim=-1)

    with torch.no_grad():
        logits = (img_emb @ text_embs.T) * 100
        probs  = F.softmax(logits, dim=-1)[0].cpu().numpy()

    best_idx = int(probs.argmax())
    return mid_names[best_idx]


def detect_small_category(clip_emb: np.ndarray, major_category: str, middle_category: str) -> str:
    key = (str(major_category), str(middle_category))
    if key not in _cached_small_embs:
        return ""

    small_names, text_embs = _cached_small_embs[key]

    img_emb = torch.tensor(clip_emb, dtype=torch.float32).to(device)
    if img_emb.dim() == 1:
        img_emb = img_emb.unsqueeze(0)
    img_emb = F.normalize(img_emb, dim=-1)

    with torch.no_grad():
        logits = (img_emb @ text_embs.T) * 100
        probs  = F.softmax(logits, dim=-1)[0].cpu().numpy()

    best_idx = int(probs.argmax())
    detected = small_names[best_idx]
    print(f"[소분류] {major_category}/{middle_category} → {detected} ({probs[best_idx]:.3f})")
    return detected


def extract_dalum_vit_embedding(image_pil):
    from vit.preprocess.pipeline.segmentation_processor import SegmentationProcessor
    from vit.preprocess.color.color_extractor import ColorExtractor
    from vit.preprocess.color.color_embedding import build_color_embedding
    from vit.preprocess.material.predictor import MaterialPredictor
    from vit.preprocess.material.material_postprocessor import MaterialPostProcessor
    from vit.preprocess.utils.image_enhancer import enhance_for_material

    img = cv2.cvtColor(np.array(image_pil.convert("RGB")), cv2.COLOR_RGB2BGR)

    seg_img = SegmentationProcessor().process(img)

    colors    = ColorExtractor().extract(seg_img)
    color_emb = build_color_embedding(colors)

    enhanced     = enhance_for_material(seg_img)
    material_vec = MaterialPredictor().predict(enhanced)
    material_emb = MaterialPostProcessor().process(material_vec)

    # ViT layer11 CLS 토큰으로 shape 임베딩 추출
    vit_model, vit_processor = _get_vit()
    inputs = vit_processor(images=image_pil.convert("RGB"), return_tensors="pt").to(device)
    with torch.no_grad():
        outputs   = vit_model(**inputs, output_hidden_states=True)
        shape_emb = outputs.hidden_states[11][:, 0, :].cpu().numpy()[0].astype("float32")

    return np.concatenate([color_emb, shape_emb, material_emb]).astype("float32").reshape(1, -1)


# MMR 중복 제거

def lab_color_sim(q_lab: np.ndarray, db_lab: np.ndarray, achromatic: bool = False) -> float:
    """CIE76 ΔE 기반 색상 유사도. sigma=10 가우시안 변환 → [0, 1]
    achromatic=True 시 a/b 성분 2.5배 가중 (웜/쿨 색조 편차 강조)"""
    dL = float(q_lab[0] - db_lab[0])
    da = float(q_lab[1] - db_lab[1])
    db_ = float(q_lab[2] - db_lab[2])
    if achromatic:
        delta_e = float(np.sqrt(dL ** 2 + 2.5 * da ** 2 + 2.5 * db_ ** 2))
    else:
        delta_e = float(np.sqrt(dL ** 2 + da ** 2 + db_ ** 2))
    return float(np.exp(-delta_e / 10.0))


def mmr_dedup(results):
    sel, sel_embs = [], []
    for item in results:
        emb  = clip_image_db[item["_db_idx"]].astype("float32")
        norm = emb / (np.linalg.norm(emb) + 1e-8)
        if not any(np.dot(norm, s) >= MMR_THRESHOLD for s in sel_embs):
            sel.append(item)
            sel_embs.append(norm)
    return sel


# 재랭킹

def rerank(results, dalum_emb, design_probs, q_color_probs=None, q_lab=None, material_gated=False, major_category=None):
    q_color    = dalum_emb[0, :768]
    q_color    = q_color / (np.linalg.norm(q_color) + 1e-8)
    q_shape    = dalum_emb[0, 768:1536]
    q_shape    = q_shape / (np.linalg.norm(q_shape) + 1e-8)
    q_material = dalum_emb[0, 1536:]
    q_material = q_material / (np.linalg.norm(q_material) + 1e-8)
    q_design   = design_probs / (design_probs.sum() + 1e-8)
    _q_top_design_name = DESIGN_NAMES[int(np.argmax(q_design))]
    _is_plain_query    = _q_top_design_name in _PLAIN_DESIGN_NAMES
    _pat_idx_arr       = np.array(_PATTERN_DESIGN_INDICES, dtype=np.int32)

    _rc_chroma = float(np.sqrt(float(q_lab[1])**2 + float(q_lab[2])**2)) if q_lab is not None else 0.0
    if material_gated:
        _mode = "material"
    elif _rc_chroma > 10.0:
        _mode = "chromatic"
    else:
        _mode = "default"

    _wt = _CATEGORY_WEIGHTS.get(str(major_category) if major_category else "", _FALLBACK_WEIGHTS)[_mode]
    _W_CLIP_IMAGE  = _wt["clip_image"]
    _W_COLOR       = _wt["vit_color"]
    _W_SHAPE       = _wt["shape"]
    _W_MATERIAL    = _wt["material"]
    _W_CLIP_DESIGN = _wt["clip_design"]
    _W_CLIP_COLOR  = _wt["clip_color"]
    _W_LAB_COLOR   = _wt["lab"]
    print(f"[RERANK] cat={major_category} mode={_mode} shape={_W_SHAPE} clip_img={_W_CLIP_IMAGE} lab={_W_LAB_COLOR}")

    # w_lab / w_clip_clr: LAB DB 존재 여부에 따라 가중치 재분배
    if q_lab is not None and mean_lab_db is not None:
        _w_lab      = _W_LAB_COLOR
        _w_clip_clr = _W_CLIP_COLOR
    else:
        _w_lab      = 0.0
        _w_clip_clr = _W_CLIP_COLOR + _W_LAB_COLOR

    # 무지 쿼리: 후보 집합 내 min-max 정규화 → 가장 무지한 아이템=1.0, 가장 패턴한 아이템=0.0
    _design_db_ok = clip_design_db is not None
    if _is_plain_query and _design_db_ok and len(results) > 1:
        _all_db_idxs = np.array([item["_db_idx"] for item in results], dtype=np.int32)
        _all_ps      = clip_design_db[_all_db_idxs][:, _pat_idx_arr].sum(axis=1)
        _ps_min      = float(_all_ps.min())
        _ps_range    = max(0.01, float(_all_ps.max()) - _ps_min)
    else:
        _ps_min, _ps_range = 0.0, 1.0

    for item in results:
        db_idx = item["_db_idx"]
        db_vit = dalum_vit_db[db_idx].astype("float32")

        # 색상 유사도: ViT layer3 cosine (768-dim)
        db_color  = db_vit[:768] / (np.linalg.norm(db_vit[:768]) + 1e-8)
        color_sim = max(0.0, float(np.dot(q_color, db_color)))

        # 형태 유사도: ViT layer11 cosine (768-dim)
        db_shape  = db_vit[768:1536] / (np.linalg.norm(db_vit[768:1536]) + 1e-8)
        shape_sim = max(0.0, float(np.dot(q_shape, db_shape)))

        # 소재 유사도 (33-dim)
        db_mat       = db_vit[1536:] / (np.linalg.norm(db_vit[1536:]) + 1e-8)
        material_sim = float(np.dot(q_material, db_mat))

        # CLIP 디자인 유사도 (DB 호환 시에만 계산)
        if not _design_db_ok:
            design_sim = 0.5  # 디자인 DB 미갱신 시 중립값
        elif _is_plain_query:
            db_pattern_sum = float(clip_design_db[db_idx][_pat_idx_arr].sum())
            design_sim = max(0.0, 1.0 - (db_pattern_sum - _ps_min) / _ps_range)
        else:
            db_d       = clip_design_db[db_idx] / (clip_design_db[db_idx].sum() + 1e-8)
            top2_idx   = np.argsort(q_design)[-2:]
            top2_w     = q_design[top2_idx] / (q_design[top2_idx].sum() + 1e-8)
            design_sim = float(np.dot(top2_w, db_d[top2_idx]))

        # CLIP 색상 분포 유사도
        if q_color_probs is not None and _db_color_probs is not None:
            db_color_p     = _db_color_probs[db_idx]
            clip_color_sim = float(np.dot(q_color_probs, db_color_p))
        else:
            clip_color_sim = 0.0

        # 픽셀 평균 LAB 유사도
        if q_lab is not None and mean_lab_db is not None:
            lab_sim = lab_color_sim(q_lab, mean_lab_db[db_idx], achromatic=(_rc_chroma <= 10.0))
        else:
            lab_sim = 0.0

        _final = (
            _W_CLIP_IMAGE  * item["faiss_score"]
            + _W_COLOR       * color_sim
            + _W_SHAPE       * shape_sim
            + _W_MATERIAL    * material_sim
            + _W_CLIP_DESIGN * design_sim
            + _w_clip_clr    * clip_color_sim
            + _w_lab         * lab_sim
        )
        item["final_score"] = _final

        # 공개 점수 (내부 세부 점수 대신 4개만 노출)
        _color_w_sum = _W_COLOR + _w_lab + _w_clip_clr
        _c_score = round((_W_COLOR * color_sim + _w_lab * lab_sim + _w_clip_clr * clip_color_sim) / max(0.01, _color_w_sum), 4)
        _m_score = round(float(material_sim), 4)
        _d_score = round(float(design_sim), 4)
        item["color_score"]    = _c_score
        item["material_score"] = _m_score
        item["design_score"]   = _d_score
        item["total_score"]    = round(float(_final), 4)
        item["_shape_sim"]     = round(float(shape_sim), 4)
        item["_clip_image"]    = round(float(item["faiss_score"]), 4)
        item["_lab_sim"]       = round(float(lab_sim), 4)

    results.sort(key=lambda x: x["final_score"], reverse=True)

    if q_lab is not None:
        print(f"[QUERY-LAB] L={q_lab[0]:.1f} a={q_lab[1]:.1f} b={q_lab[2]:.1f} chroma={_rc_chroma:.1f}")
    print("[DEBUG] top10 scores:")
    for i, r in enumerate(results[:10], 1):
        db_idx = r["_db_idx"]
        if q_lab is not None and mean_lab_db is not None:
            db_lab = mean_lab_db[db_idx]
            delta_e = float(np.sqrt(np.sum((q_lab - db_lab) ** 2)))
            da = float(q_lab[1] - db_lab[1])
            db_b = float(q_lab[2] - db_lab[2])
            delta_ab = float(np.sqrt(da ** 2 + db_b ** 2))
            lab_str = (f" | L={db_lab[0]:.1f} a={db_lab[1]:.1f} b={db_lab[2]:.1f}"
                       f" ΔE={delta_e:.1f} Δab={delta_ab:.1f}")
        else:
            lab_str = ""
        print(f"  [{i:2d}] pid={r['product_id']} "
              f"clip={r.get('_clip_image', 0):.3f} shape={r.get('_shape_sim', 0):.3f} "
              f"mat={r['material_score']:.3f} design={r['design_score']:.3f} "
              f"color={r['color_score']:.3f} lab={r.get('_lab_sim', 0):.3f} "
              f"total={r['total_score']:.3f}{lab_str}")

    return results

def extract_mean_lab(image_pil):
    img = cv2.cvtColor(np.array(image_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    pixels = img[gray < 240]
    if len(pixels) < 100:
        return np.array([50.0, 0.0, 0.0], dtype=np.float32)
    gray_vals = (0.299 * pixels[:, 2].astype(np.float32)
                 + 0.587 * pixels[:, 1].astype(np.float32)
                 + 0.114 * pixels[:, 0].astype(np.float32))
    if float(np.percentile(gray_vals, 95)) - float(np.median(gray_vals)) > 80:
        filtered = pixels[gray_vals <= float(np.percentile(gray_vals, 85))]
        if len(filtered) < 50:
            filtered = pixels
    else:
        filtered = pixels
    lab_pixels = cv2.cvtColor(
        filtered.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB
    ).reshape(-1, 3).astype(np.float32)
    n_colors = min(3, max(1, len(lab_pixels) // 100))
    km = KMeans(n_clusters=n_colors, random_state=42, n_init=5, max_iter=100)
    km.fit(lab_pixels)
    counts = np.bincount(km.labels_, minlength=n_colors)
    ratios = counts / counts.sum()
    weighted = np.sum(km.cluster_centers_ * ratios[:, np.newaxis], axis=0)
    L = float(weighted[0]) * 100.0 / 255.0
    a = float(weighted[1]) - 128.0
    b = float(weighted[2]) - 128.0
    return np.array([L, a, b], dtype=np.float32)

# 추천

def recommend_from_embedding(clip_emb, color_emb, shape_emb, material_dict, design_probs, top_k=10, major_category=None, middle_category=None, small_category=None, lab_color=None):
    if faiss_indices is None:
        raise RuntimeError("듀프 임베딩 DB가 로드되지 않았습니다. build_clip.py를 먼저 실행하세요.")

    clip_arr = np.array(clip_emb, dtype="float32").reshape(1, -1)

    color_arr = np.array(color_emb, dtype="float32")
    shape_arr = np.array(shape_emb, dtype="float32")
    if isinstance(material_dict, dict):
        material_arr = np.array(list(material_dict.values()), dtype="float32")
    else:
        material_arr = np.array(material_dict, dtype="float32")
    dalum_arr = np.concatenate([color_arr, shape_arr, material_arr]).reshape(1, -1)

    design_probs_arr = np.array(design_probs, dtype="float32")

    query_vec = clip_arr.copy()
    faiss.normalize_L2(query_vec)

    cat_key = str(major_category) if major_category else None

    # ── 중분류 자동 보정: hooded 디자인 감지 시 SWEATSHIRT → HOODIE ────
    _hooded_idx = DESIGN_NAMES.index("hooded") if "hooded" in DESIGN_NAMES else -1
    if (_hooded_idx >= 0
            and str(middle_category) == "SWEATSHIRT"
            and float(np.array(design_probs, dtype="float32")[_hooded_idx]) > 0.20):
        _hooded_prob = float(np.array(design_probs, dtype="float32")[_hooded_idx])
        print(f"[CATEGORY-CORRECT] hooded={_hooded_prob:.3f} → SWEATSHIRT → HOODIE 보정")
        middle_category = "HOODIE"

    mid_key = (str(major_category), str(middle_category)) if major_category and middle_category else None

    db_index_list = None  # 명시적 초기화

    # ── 소분류 인덱스 힌트 계산 ─────────────────────────────────────────
    # design_probs에서 소재 top-1을 보고 DB small_category 키워드 결정
    _design_arr_pre = np.array(design_probs, dtype="float32")
    _design_arr_pre = _design_arr_pre / (_design_arr_pre.sum() + 1e-8)
    _pre_top_idx    = int(_design_arr_pre.argmax())
    _pre_top_name   = DESIGN_NAMES[_pre_top_idx]
    _pre_top_prob   = float(_design_arr_pre[_pre_top_idx])
    _small_hints    = (
        _DESIGN_TO_SMALL_HINT.get(_pre_top_name, [])
        if _pre_top_name in _MATERIAL_DESIGN_NAMES and _pre_top_prob > 0.10
        else []
    )

    # 소분류 자동 감지 (파라미터 미전달 시)
    if not small_category and major_category and middle_category:
        small_category = detect_small_category(clip_arr[0], major_category, middle_category)

    # 0순위 → 소분류 인덱스 (자동 감지 또는 직접 지정)
    if small_category and faiss_small_indices and major_category and middle_category:
        _skey = (str(major_category), str(middle_category), str(small_category))
        if _skey in faiss_small_indices:
            _sidx, _sdb_idxs = faiss_small_indices[_skey]
            if len(_sdb_idxs) >= top_k:
                search_k = min(len(_sdb_idxs), top_k * 400)
                distances, local_indices = _sidx.search(query_vec, search_k)
                db_index_list = [(int(_sdb_idxs[li]), float(sc))
                                 for li, sc in zip(local_indices[0], distances[0]) if li >= 0]
                print(f"[검색] 소분류={small_category} ({len(_sdb_idxs)}개)")

    # 1순위 → 소분류 인덱스 (소재 힌트 기반, small_category 미사용 시)
    if db_index_list is None and _small_hints and faiss_small_indices and major_category and middle_category:
        for _hint in _small_hints:
            _matched_keys = [
                k for k in faiss_small_indices
                if k[0] == str(major_category)
                and k[1] == str(middle_category)
                and _hint in k[2]
            ]
            if _matched_keys:
                _skey = _matched_keys[0]
                _sidx, _sdb_idxs = faiss_small_indices[_skey]
                if len(_sdb_idxs) >= top_k:
                    search_k = min(len(_sdb_idxs), top_k * 400)
                    distances, local_indices = _sidx.search(query_vec, search_k)
                    db_index_list = [(int(_sdb_idxs[li]), float(sc))
                                     for li, sc in zip(local_indices[0], distances[0]) if li >= 0]
                    print(f"[검색] 소분류(소재힌트)={_skey[2]} ({len(_sdb_idxs)}개) ← {_pre_top_name}")
                    break

    # 2순위 → 중분류 인덱스 (소분류 미사용 시)
    if db_index_list is None and mid_key and faiss_middle_indices and mid_key in faiss_middle_indices:
        mid_index, mid_db_idxs = faiss_middle_indices[mid_key]
        if len(mid_db_idxs) >= top_k * 2:
            search_k = min(len(mid_db_idxs), top_k * 400)
            distances, local_indices = mid_index.search(query_vec, search_k)
            db_index_list = [(int(mid_db_idxs[li]), float(sc))
                             for li, sc in zip(local_indices[0], distances[0]) if li >= 0]
            print(f"[검색] 중분류={middle_category} ({len(mid_db_idxs)}개)")

    # 3순위 → 대분류 인덱스
    if db_index_list is None:
        if cat_key and cat_key in faiss_indices:
            cat_index, cat_db_idxs = faiss_indices[cat_key]
            search_k = min(len(cat_db_idxs), top_k * 400)
            distances, local_indices = cat_index.search(query_vec, search_k)
            db_index_list = [(int(cat_db_idxs[li]), float(sc))
                             for li, sc in zip(local_indices[0], distances[0]) if li >= 0]
            print(f"[검색] 대분류={major_category} ({len(cat_db_idxs)}개) 폴백")
        else:
            # 3순위 → 전체 인덱스
            search_k = min(len(clip_image_db), top_k * 400)
            distances, indices = faiss_index_all.search(query_vec, search_k)
            db_index_list = [(int(di), float(sc))
                             for di, sc in zip(indices[0], distances[0]) if di >= 0]
            print("[검색] 전체 인덱스 폴백")

    # 쿼리 디자인 로그 (top-3, 그룹 표시)
    _q_design_probs = np.array(design_probs, dtype="float32")
    _q_design_probs = _q_design_probs / (_q_design_probs.sum() + 1e-8)
    _top3_design = np.argsort(_q_design_probs)[-3:][::-1]
    def _design_group(n):
        if n in _MATERIAL_DESIGN_NAMES: return "소재"
        if n in _SHAPE_DESIGN_NAMES:    return "형태"
        if n in _PLAIN_DESIGN_NAMES:    return "무지"
        return "패턴"
    _design_log = " | ".join(
        f"{DESIGN_NAMES[i]}[{_design_group(DESIGN_NAMES[i])}]({_q_design_probs[i]:.3f})"
        for i in _top3_design
    )
    print(f"[DESIGN] 쿼리 top-3: {_design_log}")

    # 쿼리의 CLIP 색상 분포 계산
    q_color_probs = None
    if _db_color_probs is not None:
        q_clip_t = torch.tensor(query_vec, dtype=torch.float32).to(device)
        with torch.no_grad():
            q_color_logits = (q_clip_t @ _cached_color_text_embs.T) * 100
            q_color_probs  = F.softmax(q_color_logits, dim=-1)[0].cpu().numpy().astype("float32")
        top_color_idx = int(q_color_probs.argmax())
        print(f"[COLOR] 감지된 색상: {COLOR_PROMPTS[top_color_idx]} ({q_color_probs[top_color_idx]:.3f})")

    q_lab = np.array(lab_color, dtype=np.float32) if lab_color is not None else None
    _q_chroma = float(np.sqrt(float(q_lab[1])**2 + float(q_lab[2])**2)) if q_lab is not None else 0.0
    if q_lab is not None:
        _achromatic_str = "무채색" if _q_chroma <= 10.0 else "유채색"
        print(f"[QUERY-LAB] L={q_lab[0]:.1f} a={q_lab[1]:.1f} b={q_lab[2]:.1f} "
              f"chroma={_q_chroma:.1f} → {_achromatic_str}")

    # 게이트 1: 동일 제품 제외
    before = len(db_index_list)
    db_index_list = [(di, sc) for di, sc in db_index_list if sc < SELF_MATCH_THRESHOLD]
    if len(db_index_list) < before:
        print(f"[GATE-SAME] {before - len(db_index_list)}개 제외")

    # 게이트 2: 색상 (LAB ΔE + 채도 기반)
    if q_lab is not None and mean_lab_db is not None:
        def _de(di): return float(np.sqrt(np.sum((q_lab - mean_lab_db[di]) ** 2)))

        if _q_chroma > 10.0:
            # 유채색 쿼리 (초록/빨강/파랑 등)
            # 채도 게이트: DB 채도가 쿼리 채도의 70%~180% 범위만 허용
            _chroma_min = _q_chroma * 0.7
            _chroma_max = _q_chroma * 1.8
            _chroma_filtered = [
                (di, sc) for di, sc in db_index_list
                if _chroma_min <= float(np.sqrt(float(mean_lab_db[di][1])**2 + float(mean_lab_db[di][2])**2)) <= _chroma_max
            ]
            print(f"[GATE-CHROMA] q_chroma={_q_chroma:.1f} range=[{_chroma_min:.1f},{_chroma_max:.1f}] → {len(_chroma_filtered)}개")
            if len(_chroma_filtered) >= 1:
                db_index_list = _chroma_filtered

            # 명도(L) 범위 게이트
            _L_q = float(q_lab[0])
            _L_RANGE = 8.0
            _L_filtered = [
                (di, sc) for di, sc in db_index_list
                if abs(float(mean_lab_db[di][0]) - _L_q) < _L_RANGE
            ]
            print(f"[GATE-LIGHTNESS] L={_L_q:.1f} ±{_L_RANGE} → {len(_L_filtered)}개")
            if len(_L_filtered) >= 1:
                db_index_list = _L_filtered

            # LAB ΔE 게이트: 유채색은 엄격하게
            LAB_GATE = 12.0
            filtered = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE]
            print(f"[GATE-COLOR] chroma={_q_chroma:.1f} ΔE<{LAB_GATE} → {len(filtered)}개")
            if len(filtered) >= top_k:
                db_index_list = filtered
            else:
                LAB_GATE2 = 15.0
                filtered2 = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE2]
                if len(filtered2) >= top_k:
                    db_index_list = filtered2
                    print(f"[GATE-COLOR] ΔE<{LAB_GATE2} (완화) → {len(db_index_list)}개")
                else:
                    LAB_GATE3 = 18.0
                    db_index_list = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE3]
                    print(f"[GATE-COLOR] ΔE<{LAB_GATE3} (최대완화) → {len(db_index_list)}개")
        else:
            # 무채색 쿼리 (black/gray/white 등)
            # OUTER 무채색: ΔE<28 이상으로 완화하지 않음
            _achromatic_max_gate = 20.0 if str(major_category) == "OUTER" else 22.0
            LAB_GATE = 14.0
            filtered = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE]
            print(f"[GATE-COLOR] chroma={_q_chroma:.1f} ΔE<{LAB_GATE} → {len(filtered)}개")
            if len(filtered) >= top_k * 3:
                db_index_list = filtered
            else:
                LAB_GATE2 = 20.0
                filtered2 = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE2]
                if len(filtered2) >= top_k * 2:
                    db_index_list = filtered2
                    print(f"[GATE-COLOR] ΔE<{LAB_GATE2} (완화) → {len(db_index_list)}개")
                elif _achromatic_max_gate > 28.0:
                    LAB_GATE3 = _achromatic_max_gate
                    db_index_list = [(di, sc) for di, sc in db_index_list if _de(di) < LAB_GATE3]
                    print(f"[GATE-COLOR] ΔE<{LAB_GATE3} (최대완화) → {len(db_index_list)}개")
                else:
                    db_index_list = filtered2  # OUTER: ΔE<28 이상 허용 안 함
                    print(f"[GATE-COLOR] OUTER 무채색 ΔE<28 상한 고정 → {len(db_index_list)}개")

            # 무채색 a-b 편차 게이트: 웜/브라운 색조 제거
            # 쿼리가 중립 블랙/그레이인데 DB 아이템이 warm brown(a>0, b>0)인 경우 차단
            _AB_GATE = 3.5 if str(major_category) == "OUTER" else 4.5
            _ab_filtered = [
                (di, sc) for di, sc in db_index_list
                if float(np.sqrt(
                    (float(q_lab[1]) - float(mean_lab_db[di][1])) ** 2 +
                    (float(q_lab[2]) - float(mean_lab_db[di][2])) ** 2
                )) < _AB_GATE
            ]
            print(f"[GATE-AB] 무채색 Δab<{_AB_GATE} → {len(_ab_filtered)}개")
            if len(_ab_filtered) >= top_k:
                db_index_list = _ab_filtered

    # CLIP 색상 분포 게이트
    # 스튜디오 조명 영향으로 LAB이 차콜처럼 측정되는 검정 제품 (3팩 등) 제거
    # 115555/116436 같은 경우: lab_sim=0.9 이지만 clip_color=0.072 (낮음)
    if q_color_probs is not None and _db_color_probs is not None:
        cc_arr  = np.array([float(np.dot(q_color_probs, _db_color_probs[di]))
                            for di, _ in db_index_list], dtype=np.float32)
        # 유채색 쿼리: 하위 50% 제거
        # 무채색 쿼리: 하위 25% 제거
        _cc_percentile = 50 if _q_chroma > 10.0 else 25
        CC_GATE = float(np.percentile(cc_arr, _cc_percentile))
        filtered = [(di, sc) for (di, sc), cc in zip(db_index_list, cc_arr) if cc >= CC_GATE]
        _cc_min = top_k if _q_chroma > 10.0 else top_k * 2
        if len(filtered) >= _cc_min:
            db_index_list = filtered
            print(f"[GATE-CLIP-COLOR] clip_color>={CC_GATE:.3f} ({_cc_percentile}pct) → {len(db_index_list)}개")

    # 소재 임베딩 게이트 (OUTER + 무채색 전용)
    _outer_achromatic = (str(major_category) == "OUTER" and _q_chroma <= 10.0)
    if _outer_achromatic and dalum_vit_db is not None:
        _q_mat_norm = material_arr / (np.linalg.norm(material_arr) + 1e-8)
        _mat_sims = np.array([
            float(np.dot(_q_mat_norm,
                         dalum_vit_db[di][1536:] / (np.linalg.norm(dalum_vit_db[di][1536:]) + 1e-8)))
            for di, _ in db_index_list
        ], dtype=np.float32)
        _MAT_GATE = float(np.percentile(_mat_sims, 75))
        _mat_filtered = [(di, sc) for (di, sc), ms in zip(db_index_list, _mat_sims) if ms >= _MAT_GATE]
        if len(_mat_filtered) >= top_k:
            db_index_list = _mat_filtered
            print(f"[GATE-MATERIAL] OUTER 무채색 mat_sim>={_MAT_GATE:.3f} (top35%) → {len(db_index_list)}개")

    # 디자인
    _q_design_arr    = np.array(design_probs, dtype="float32")
    _q_design_arr    = _q_design_arr / (_q_design_arr.sum() + 1e-8)
    _top_design_idx  = int(_q_design_arr.argmax())
    _top_design_prob = float(_q_design_arr[_top_design_idx])

    _top_design_name = DESIGN_NAMES[_top_design_idx]
    _material_gated  = False
    _is_outer        = (str(major_category) == "OUTER")

    def _apply_leather_exclusion_gates():
        """leather 쿼리: nylon/denim 상위 40% 제거 (색상 무관 공통 적용)"""
        nonlocal db_index_list
        if clip_design_db is None:
            return
        if "nylon" in DESIGN_NAMES:
            _nylon_idx = DESIGN_NAMES.index("nylon")
            _nylon_scores = np.array([float(clip_design_db[di][_nylon_idx]) for di, _ in db_index_list], dtype=np.float32)
            _NYLON_EXCL = float(np.percentile(_nylon_scores, 60))
            _anti_nylon = [(di, sc) for (di, sc), ns in zip(db_index_list, _nylon_scores) if ns < _NYLON_EXCL]
            if len(_anti_nylon) >= top_k:
                db_index_list = _anti_nylon
                print(f"[GATE-NYLON] leather nylon<{_NYLON_EXCL:.3f} → {len(db_index_list)}개")
        if "denim" in DESIGN_NAMES:
            _denim_idx = DESIGN_NAMES.index("denim")
            _denim_scores = np.array([float(clip_design_db[di][_denim_idx]) for di, _ in db_index_list], dtype=np.float32)
            _DENIM_EXCL = float(np.percentile(_denim_scores, 60))
            _anti_denim = [(di, sc) for (di, sc), ds in zip(db_index_list, _denim_scores) if ds < _DENIM_EXCL]
            if len(_anti_denim) >= top_k:
                db_index_list = _anti_denim
                print(f"[GATE-DENIM] leather denim<{_DENIM_EXCL:.3f} → {len(db_index_list)}개")

    # ── 케이스 A: OUTER + 무채색 ────────────────────────────────────────
    if _outer_achromatic:
        _material_gated = True
        if _top_design_name in _MATERIAL_DESIGN_NAMES and _top_design_prob > 0.15 and clip_design_db is not None:
            db_design_scores = np.array([float(clip_design_db[di][_top_design_idx]) for di, _ in db_index_list], dtype=np.float32)
            DESIGN_GATE = max(0.02, float(np.percentile(db_design_scores, 70)))
            filtered = [(di, sc) for (di, sc), ds in zip(db_index_list, db_design_scores) if ds >= DESIGN_GATE]
            if len(filtered) >= top_k:
                db_index_list = filtered
                print(f"[GATE-DESIGN] OUTER 무채색+소재({_top_design_name},{_top_design_prob:.2f}) "
                      f"clip_design>={DESIGN_GATE:.3f} → {len(db_index_list)}개")
            else:
                print(f"[GATE-DESIGN] OUTER 무채색 소재게이트 후보 부족({len(filtered)}개) → 스킵")
            if _top_design_name == "leather":
                _apply_leather_exclusion_gates()
        else:
            print(f"[GATE-DESIGN] OUTER 무채색 → 소재게이트 스킵 (prob={_top_design_prob:.3f})")

    # ── 케이스 B: OUTER + 유채색 + leather (무채색 블록에서 미처리) ─────
    elif _is_outer and _top_design_name == "leather" and _top_design_prob > 0.15 and clip_design_db is not None:
        _material_gated = True
        db_design_scores = np.array([float(clip_design_db[di][_top_design_idx]) for di, _ in db_index_list], dtype=np.float32)
        DESIGN_GATE = max(0.02, float(np.percentile(db_design_scores, 70)))
        filtered = [(di, sc) for (di, sc), ds in zip(db_index_list, db_design_scores) if ds >= DESIGN_GATE]
        if len(filtered) >= top_k:
            db_index_list = filtered
            print(f"[GATE-DESIGN] OUTER 유채색+leather({_top_design_prob:.2f}) "
                  f"clip_design>={DESIGN_GATE:.3f} → {len(db_index_list)}개")
        else:
            print(f"[GATE-DESIGN] OUTER 유채색 leather 후보 부족({len(filtered)}개) → 스킵")
        _apply_leather_exclusion_gates()

    # ── 케이스 C: 그 외 일반 디자인 게이트 ──────────────────────────────
    elif _top_design_prob > 0.10 and clip_design_db is not None:
        if _top_design_name in _MATERIAL_DESIGN_NAMES:
            db_design_scores = np.array([float(clip_design_db[di][_top_design_idx]) for di, _ in db_index_list], dtype=np.float32)
            DESIGN_GATE = max(0.03, float(np.percentile(db_design_scores, 70)))
            filtered = [(di, sc) for di, sc in db_index_list if float(clip_design_db[di][_top_design_idx]) >= DESIGN_GATE]
            print(f"[GATE-DESIGN] 쿼리=소재({_top_design_name},{_top_design_prob:.2f}) gate={DESIGN_GATE:.3f} → 통과 {len(filtered)}/{len(db_index_list)}개")
        elif _top_design_name in _SHAPE_DESIGN_NAMES:
            db_design_scores = np.array([float(clip_design_db[di][_top_design_idx]) for di, _ in db_index_list], dtype=np.float32)
            DESIGN_GATE = max(0.02, float(np.percentile(db_design_scores, 60)))
            filtered = [(di, sc) for di, sc in db_index_list if float(clip_design_db[di][_top_design_idx]) >= DESIGN_GATE]
            print(f"[GATE-DESIGN] 쿼리=형태({_top_design_name},{_top_design_prob:.2f}) gate={DESIGN_GATE:.3f} → 통과 {len(filtered)}/{len(db_index_list)}개")
        elif _top_design_name in _PLAIN_DESIGN_NAMES:
            db_pattern_sums = np.array([float(clip_design_db[di][_PATTERN_DESIGN_INDICES].sum()) for di, _ in db_index_list], dtype=np.float32)
            PLAIN_GATE = float(np.percentile(db_pattern_sums, 50))
            filtered = [(di, sc) for di, sc in db_index_list if float(clip_design_db[di][_PATTERN_DESIGN_INDICES].sum()) <= PLAIN_GATE]
            print(f"[GATE-DESIGN] 쿼리=무지({_top_design_name},{_top_design_prob:.2f}) pattern_gate<={PLAIN_GATE:.3f} → 통과 {len(filtered)}/{len(db_index_list)}개")
        else:
            db_design_scores = np.array([float(clip_design_db[di][_top_design_idx]) for di, _ in db_index_list], dtype=np.float32)
            DESIGN_GATE = max(0.03, float(np.percentile(db_design_scores, 70)))
            filtered = [(di, sc) for di, sc in db_index_list if float(clip_design_db[di][_top_design_idx]) >= DESIGN_GATE]
            print(f"[GATE-DESIGN] 쿼리=패턴({_top_design_name},{_top_design_prob:.2f}) gate={DESIGN_GATE:.3f} → 통과 {len(filtered)}/{len(db_index_list)}개")

        if len(filtered) >= 3:
            db_index_list = filtered
            _material_gated = (_top_design_name in _MATERIAL_DESIGN_NAMES)
        else:
            print(f"[GATE-DESIGN] 후보 부족({len(filtered)}개) → 게이트 스킵")

    # 결과 목록 구성
    results = []
    for db_idx, score in db_index_list:
        row = metadata.iloc[db_idx]
        results.append({
            "product_id"     : int(row["product_id"]),
            "major_category" : row.get("major_category", ""),
            "middle_category": row.get("middle_category", ""),
            "image_type"     : row.get("image_type", ""),
            "faiss_score"    : score,
            "color_sim"      : 0.0,
            "design_sim"     : 0.0,
            "clip_color_sim" : 0.0,
            "final_score"    : score,
            "_db_idx"        : db_idx,
        })

    results = mmr_dedup(results)
    results = rerank(results, dalum_arr, design_probs_arr, q_color_probs, q_lab,
                     material_gated=_material_gated, major_category=major_category)

    # 내부용 키 제거, 공개 필드만 유지
    _internal_keys = ["_db_idx", "faiss_score", "color_sim", "shape_sim",
                      "clip_color_sim", "lab_sim", "design_sim", "final_score",
                      "_shape_sim", "_clip_image", "_lab_sim"]
    for item in results:
        for k in _internal_keys:
            item.pop(k, None)

    final = results[:top_k]
    color_insufficient = len(final) < max(1, top_k // 2)
    return final, color_insufficient


def recommend(image, top_k=10):
    """
    image: 이미지 파일 경로(str) 또는 PIL.Image
    반환: (results, design_scores, top_design)
    """
    if isinstance(image, str):
        image_pil = Image.open(image).convert("RGB")
    else:
        image_pil = image.convert("RGB")

    clip_emb, design_scores, design_probs = extract_clip_features(image_pil)
    dalum_emb = extract_dalum_vit_embedding(image_pil)

    major_cat  = detect_major_category(clip_emb=clip_emb)
    middle_cat = detect_middle_category(clip_emb=clip_emb, major_category=major_cat)
    q_lab      = extract_mean_lab(image_pil)

    color_emb    = dalum_emb[0, :768]
    shape_emb    = dalum_emb[0, 768:1536]
    material_emb = dalum_emb[0, 1536:]

    results, _ = recommend_from_embedding(
        clip_emb, color_emb, shape_emb, material_emb, design_probs,
        top_k=top_k,
        major_category=major_cat,
        middle_category=middle_cat,
        lab_color=q_lab,
    )

    top_design = max(design_scores, key=design_scores.get)
    return results, design_scores, top_design
