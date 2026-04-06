#!/usr/bin/env python3
"""
최종 추천 시스템 v3

구조:
  Segformer       → 쿼리 배경제거
  CLIP 이미지     → FAISS 검색 (의미/패턴/형태 통합)
  LAB 공간분할    → 색상 재랭킹 (3×3 구역별 위치+색상)
  ViT layer11     → 형태/실루엣 재랭킹
  CLIP 디자인     → 디자인 라벨 재랭킹

최종 점수 = CLIP이미지 × 0.50
           + LAB색상    × 0.20
           + ViT형태    × 0.15
           + CLIP디자인 × 0.15

사용법:
    python recommend_final.py image.png 10
    python recommend_final.py image.png 10 10000 100000
"""

import torch
import torch.nn.functional as F
from transformers import (ViTModel, ViTImageProcessor,
                          CLIPModel, CLIPProcessor,
                          AutoImageProcessor, AutoModelForSemanticSegmentation)
from PIL import Image
import numpy as np
import pandas as pd
import faiss
import cv2
from skimage.color import rgb2lab
from skimage.morphology import convex_hull_image
import re, sys, os

# ==================== 파라미터 ====================

W_CLIP_IMAGE  = 0.50
W_LAB_COLOR   = 0.20
W_VIT         = 0.15
W_CLIP_DESIGN = 0.15

MMR_THRESHOLD      = 0.97
DESIGN_DISPLAY_THR = 0.15

# LAB 공간분할 설정
GRID          = 3
N_COLORS      = 3
FEAT_PER_ZONE = N_COLORS * 4  # L, a, b, 비율 × 3색
TOTAL_DIM     = GRID * GRID * FEAT_PER_ZONE  # 108
IMG_SIZE      = 64
BG_THR        = 230

# ==================== 경로 ====================

_BASE = os.path.dirname(os.path.abspath(__file__))

METADATA_PATH    = os.path.join(_BASE, 'final_models', 'embeddings_metadata.csv')
CLIP_IMAGE_PATH  = os.path.join(_BASE, 'embeddings_clip_image.npy')
CLIP_DESIGN_PATH = os.path.join(_BASE, 'embeddings_clip_design.npy')
LAB_SPATIAL_PATH = os.path.join(_BASE, 'embeddings_lab_spatial.npy')
VIT_SHAPE_PATH   = os.path.join(_BASE, 'embeddings_vit.npy')
PRODUCTS_PATH    = os.path.join(_BASE, 'all_products_id.csv')

# ==================== CLIP 디자인 (37개) ====================

DESIGN_PROMPTS = {
    "solid"        : "a solid color clothing with no pattern",
    "color_block"  : "a clothing with color block design",
    "gradient"     : "a clothing with gradient or ombre color effect",
    "striped"      : "a clothing with stripe pattern",
    "checkered"    : "a clothing with check or plaid pattern",
    "argyle"       : "a clothing with argyle diamond pattern",
    "houndstooth"  : "a clothing with houndstooth pattern",
    "polka_dot"    : "a clothing with polka dot pattern",
    "geometric"    : "a clothing with geometric shapes pattern",
    "floral"       : "a clothing with floral or flower pattern",
    "paisley"      : "a clothing with paisley or abstract pattern",
    "animal_print" : "a clothing with animal print like leopard or zebra",
    "camouflage"   : "a clothing with camouflage pattern",
    "tie_dye"      : "a clothing with tie dye pattern",
    "logo_text"    : "a clothing with logo or text print",
    "graphic"      : "a clothing with graphic or illustration print",
    "character"    : "a clothing with cartoon character, mascot, or animal graphic print",
    "heart"        : "a clothing with heart shape print",
    "star"         : "a clothing with star shape print",
    "embroidery"   : "a clothing with embroidery or embroidered detail",
    "rhinestone"   : "a clothing with rhinestones studs or jewel details",
    "ribbon_bow"   : "a clothing with ribbon or bow detail",
    "fringe"       : "a clothing with fringe or tassel detail",
    "metallic"     : "a clothing with shiny metallic sequin or glitter",
    "pleated"      : "a clothing with pleated or ruffle details",
    "varsity"      : "a varsity or stadium jacket with contrast sleeves",
    "washed"       : "a washed distressed or vintage treated clothing",
    "denim"        : "a denim clothing like jeans or denim jacket",
    "knit"         : "a knit or cable knit sweater clothing",
    "leather"      : "a clothing made of leather or faux leather",
    "fur"          : "a clothing made of fluffy fur or faux fur",
    "fleece"       : "a clothing made of cozy fleece material",
    "velvet"       : "a clothing made of velvet or velour fabric",
    "silk_satin"   : "a clothing made of glossy silk or satin fabric",
    "linen"        : "a clothing made of breathable linen fabric",
    "sheer"        : "a sheer or transparent mesh clothing",
    "lace"         : "a clothing with lace detail or lace fabric",
}

DESIGN_NAMES = list(DESIGN_PROMPTS.keys())
DESIGN_TEXTS = list(DESIGN_PROMPTS.values())

LABEL_NAMES  = ['Background','Hat','Hair','Sunglasses','Upper-clothes',
                'Skirt','Pants','Dress','Belt','Left-shoe',
                'Right-shoe','Face','Left-leg','Right-leg','Left-arm',
                'Right-arm','Bag','Scarf']
CLOTH_LABELS = ['Hat','Upper-clothes','Skirt','Pants','Dress',
                'Belt','Left-shoe','Right-shoe','Bag','Scarf']

# ==================== 초기화 ====================

print("🚀 최종 추천 시스템 v3 초기화...\n")
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"   디바이스: {device}\n")

print("1️⃣  Segformer 로드...")
seg_processor = AutoImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
seg_model     = AutoModelForSemanticSegmentation.from_pretrained(
                    "mattmdjaga/segformer_b2_clothes").to(device)
seg_model.eval()
print("   ✅ 완료")

print("2️⃣  ViT 로드...")
vit_model     = ViTModel.from_pretrained("google/vit-base-patch16-224")
vit_processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
vit_model.eval()
print("   ✅ 완료")

print("3️⃣  CLIP 로드...")
clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
clip_model.eval()
with torch.no_grad():
    _text_inputs      = clip_processor(text=DESIGN_TEXTS, return_tensors="pt", padding=True)
    _cached_text_embs = F.normalize(clip_model.get_text_features(**_text_inputs), dim=-1)
print(f"   ✅ 완료")

print("4️⃣  메타데이터 & 상품정보 로드...")
metadata = pd.read_csv(METADATA_PATH)
metadata['product_id'] = metadata['product_id'].astype(str)
try:
    COLS = ['ID','쇼핑몰','대분류','중분류','카테고리','col5','col6',
            '정가','판매가','할인율','상품 URL','이미지 URL']
    df_all = pd.read_csv(PRODUCTS_PATH, sep='\t', header=0, on_bad_lines='skip')
    if len(df_all.columns) == 1:
        df_all = pd.read_csv(PRODUCTS_PATH, sep=',', header=0,
                             on_bad_lines='skip', low_memory=False)
    df_all.columns = COLS[:len(df_all.columns)]
    df_musinsa = df_all[df_all['쇼핑몰'] == 'musinsa'].copy()
    df_29cm    = df_all[df_all['쇼핑몰'] == '29cm'].copy()
    df_musinsa['상품명'] = df_musinsa['col6']
    df_musinsa['브랜드']  = df_musinsa['col5']
    df_29cm['상품명']    = df_29cm['col5']
    df_29cm['브랜드']     = df_29cm['col6']
    products_df = pd.concat([df_musinsa, df_29cm], ignore_index=True)
    products_df['ID'] = products_df['ID'].astype(str)
    products_df['price'] = pd.to_numeric(
        products_df['판매가'].astype(str).str.replace(',','').str.replace('원',''),
        errors='coerce'
    )
    print(f"   ✅ {len(products_df):,}개")
except Exception as e:
    print(f"   ⚠️  상품정보 로드 실패: {e}")
    products_df = None

print("5️⃣  임베딩 DB & FAISS 로드...")
clip_image_db  = np.load(CLIP_IMAGE_PATH, mmap_mode='r')
clip_design_db = np.load(CLIP_DESIGN_PATH, mmap_mode='r')
lab_spatial_db = np.load(LAB_SPATIAL_PATH, mmap_mode='r')
vit_shape_db   = np.load(VIT_SHAPE_PATH, mmap_mode='r')

_emb = clip_image_db.copy()
faiss.normalize_L2(_emb)
faiss_index = faiss.IndexFlatIP(512)
faiss_index.add(_emb)

category_centroids = {}
for cat in metadata['category'].unique():
    idxs = metadata[metadata['category'] == cat].index.tolist()
    c    = clip_image_db[idxs].mean(axis=0)
    category_centroids[cat] = c / (np.linalg.norm(c) + 1e-8)

print(f"   ✅ CLIP이미지 {clip_image_db.shape}")
print(f"      LAB공간분할 {lab_spatial_db.shape}")
print(f"      CLIP디자인 {clip_design_db.shape}")
print(f"      ViT형태 {vit_shape_db.shape}")
print(f"   카테고리: {list(category_centroids.keys())}")
print(f"\n✅ 초기화 완료!\n")


# ==================== 배경 제거 ====================

def remove_background(image_pil):
    inputs = seg_processor(images=image_pil, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = seg_model(**inputs)
    upsampled = F.interpolate(
        outputs.logits, size=image_pil.size[::-1],
        mode='bilinear', align_corners=False
    )
    pred_seg     = upsampled.argmax(dim=1)[0].cpu().numpy()
    product_mask = np.zeros_like(pred_seg, dtype=bool)
    for label_name in CLOTH_LABELS:
        if label_name in LABEL_NAMES:
            product_mask |= (pred_seg == LABEL_NAMES.index(label_name))

    if not product_mask.any():
        print("   ⚠️  배경제거 실패 → 원본 사용")
        return image_pil

    product_mask = convex_hull_image(product_mask)
    img_array    = np.array(image_pil.convert('RGB'))
    alpha        = np.where(product_mask, 255, 0).astype(np.uint8)
    result       = Image.fromarray(np.dstack((img_array, alpha)), 'RGBA')
    bbox = result.getbbox()
    if bbox:
        result = result.crop(bbox)
    bg = Image.new('RGB', result.size, (255, 255, 255))
    bg.paste(result, mask=result.split()[3])
    return bg


# ==================== LAB 공간분할 추출 ====================

def extract_query_lab(image_pil):
    from sklearn.cluster import KMeans
    import warnings
    warnings.filterwarnings('ignore')

    img_rgb = cv2.cvtColor(
        cv2.resize(np.array(image_pil.convert('RGB')), (IMG_SIZE, IMG_SIZE)),
        cv2.COLOR_RGB2BGR
    )
    img_rgb = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2RGB)
    h, w    = img_rgb.shape[:2]
    zone_h  = h // GRID
    zone_w  = w // GRID

    feat = []
    for row in range(GRID):
        for col in range(GRID):
            zone       = img_rgb[row*zone_h:(row+1)*zone_h,
                                 col*zone_w:(col+1)*zone_w]
            pixels_rgb = zone.reshape(-1, 3).astype(np.float32) / 255.0
            bg_mask    = np.all(pixels_rgb > BG_THR/255.0, axis=1)
            pixels_rgb = pixels_rgb[~bg_mask]

            if len(pixels_rgb) < N_COLORS:
                feat.extend([0.0] * FEAT_PER_ZONE)
                continue

            pixels_lab = rgb2lab(pixels_rgb.reshape(-1, 1, 3)).reshape(-1, 3)

            n_c = min(N_COLORS, len(pixels_lab))
            km  = KMeans(n_clusters=n_c, random_state=42,
                         n_init=5, max_iter=100).fit(pixels_lab)
            centers = km.cluster_centers_
            counts  = np.bincount(km.labels_, minlength=n_c)
            ratios  = counts / counts.sum()

            order   = np.argsort(ratios)[::-1]
            centers = centers[order]
            ratios  = ratios[order]

            zone_feat = []
            for k in range(N_COLORS):
                if k < n_c:
                    L, a, b = centers[k]
                    zone_feat.extend([
                        float(L / 100.0),
                        float((a + 128) / 255.0),
                        float((b + 128) / 255.0),
                        float(ratios[k])
                    ])
                else:
                    zone_feat.extend([0.0, 0.0, 0.0, 0.0])
            feat.extend(zone_feat)

    return np.array(feat, dtype=np.float32)


# ==================== 쿼리 특징 추출 ====================

def extract_query_features(image_pil):
    # ViT layer11
    vit_inputs = vit_processor(images=image_pil, return_tensors="pt")
    with torch.no_grad():
        outputs = vit_model(**vit_inputs, output_hidden_states=True)
        vit_vec = outputs.hidden_states[11][:, 0, :].numpy()

    # CLIP
    clip_input = clip_processor(images=image_pil, return_tensors="pt")
    with torch.no_grad():
        _img_feats = clip_model.get_image_features(**clip_input)
        if hasattr(_img_feats, 'pooler_output'):
            _img_feats = _img_feats.pooler_output
        img_emb = F.normalize(_img_feats, dim=-1)
        logits  = (img_emb @ _cached_text_embs.T) * 100
        probs   = F.softmax(logits, dim=-1)[0].cpu().numpy()

    design_scores = {name: float(p) for name, p in zip(DESIGN_NAMES, probs)}
    return {
        'vit_vec'      : vit_vec,
        'clip_img_emb' : img_emb.cpu().numpy(),
        'design_scores': design_scores,
        'design_probs' : probs,
        'top_design'   : max(design_scores, key=design_scores.get),
    }


# ==================== 카테고리 감지 ====================

def detect_category(clip_img_emb):
    q_norm = clip_img_emb / (np.linalg.norm(clip_img_emb) + 1e-8)
    scores = {cat: float(np.dot(q_norm, cen)) for cat, cen in category_centroids.items()}
    top3   = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return top3[0][0], top3


# ==================== LAB 유사도 (Delta-E 기반) ====================

def lab_similarity(q_lab, db_lab):
    """구역별 대표색 Delta-E 거리 → 유사도"""
    q_zones  = q_lab.reshape(GRID*GRID, FEAT_PER_ZONE)   # (9, 12)
    db_zones = db_lab.reshape(GRID*GRID, FEAT_PER_ZONE)  # (9, 12)

    zone_sims = []
    for q_zone, db_zone in zip(q_zones, db_zones):
        # 각 구역의 대표색 3개씩 꺼내기
        q_colors  = q_zone.reshape(N_COLORS, 4)   # (3, [L,a,b,비율])
        db_colors = db_zone.reshape(N_COLORS, 4)

        # 역정규화
        def denorm(c):
            return np.array([c[0]*100, c[1]*255-128, c[2]*255-128])

        # 대표색끼리 가중 Delta-E (비율 × 거리)
        color_sim = 0.0
        for qc in q_colors:
            q_ratio = qc[3]
            if q_ratio < 0.05:
                continue
            q_lab_val = denorm(qc)
            # DB 대표색 중 가장 가까운 색과 매칭
            best_sim = 0.0
            for dc in db_colors:
                db_ratio   = dc[3]
                db_lab_val = denorm(dc)
                delta_e    = np.sqrt(np.sum((q_lab_val - db_lab_val)**2))
                sim        = float(np.exp(-delta_e / 30.0)) * db_ratio
                best_sim   = max(best_sim, sim)
            color_sim += q_ratio * best_sim

        zone_sims.append(color_sim)

    return float(np.mean(zone_sims))


# ==================== 재랭킹 ====================

def rerank(results, feats, query_lab):
    q_vit    = feats['vit_vec'][0] / (np.linalg.norm(feats['vit_vec'][0]) + 1e-8)
    q_design = feats['design_probs'] / (feats['design_probs'].sum() + 1e-8)

    for item in results:
        db_idx = item['_db_idx']

        # LAB 색상 유사도
        lab_sim = lab_similarity(query_lab, lab_spatial_db[db_idx])

        # ViT 형태 유사도
        db_vit  = vit_shape_db[db_idx]
        db_vit  = db_vit / (np.linalg.norm(db_vit) + 1e-8)
        vit_sim = float(np.dot(q_vit, db_vit))

        # CLIP 디자인 유사도
        db_d   = clip_design_db[db_idx]
        db_d   = db_d / (db_d.sum() + 1e-8)
        dsim   = float(np.dot(q_design, db_d) /
                       (np.linalg.norm(q_design) * np.linalg.norm(db_d) + 1e-8))

        item['lab_sim']    = lab_sim
        item['vit_sim']    = vit_sim
        item['design_sim'] = dsim
        item['final_score'] = (
            W_CLIP_IMAGE  * item['faiss_score']
            + W_LAB_COLOR   * lab_sim
            + W_VIT         * vit_sim
            + W_CLIP_DESIGN * dsim
        )

    results.sort(key=lambda x: x['final_score'], reverse=True)
    return results


# ==================== 공통 디자인 ====================

def get_common_designs(query_probs, db_idx, thr=DESIGN_DISPLAY_THR):
    db_d   = clip_design_db[db_idx]
    common = []
    for i, name in enumerate(DESIGN_NAMES):
        if float(query_probs[i]) >= thr and float(db_d[i]) >= thr:
            common.append((name, float(query_probs[i]), float(db_d[i])))
    return sorted(common, key=lambda x: x[1], reverse=True)


# ==================== 유틸 ====================

def _color_name(rgb):
    r, g, b = int(rgb[0]), int(rgb[1]), int(rgb[2])
    if max(r,g,b) - min(r,g,b) < 30:
        return "검정" if max(r,g,b) < 80 else ("흰색" if min(r,g,b) > 200 else "회색")
    if r > g and r > b: return "주황" if g > 100 else "빨강"
    if g > r and g > b: return "청록" if b > 100 else "초록"
    if b > r and b > g: return "보라" if r > 100 else "파랑"
    return "갈색"

def extract_main_colors(image_pil):
    img    = np.array(image_pil.convert('RGB'))
    pixels = img.reshape(-1, 3).astype(np.float32)
    mask   = ~np.all(pixels > BG_THR, axis=1)
    pixels = pixels[mask]
    if len(pixels) < 5:
        return []
    from sklearn.cluster import KMeans
    km     = KMeans(n_clusters=3, random_state=42, n_init=5).fit(pixels)
    counts = np.bincount(km.labels_)
    idx    = np.argsort(counts)[::-1]
    return [_color_name(km.cluster_centers_[i]) for i in idx]

def _strip_color(name):
    if not name or pd.isna(name): return ""
    name = str(name).lower()
    for c in ['검정','흰색','빨강','파랑','베이지','카키','네이비','그레이','올리브',
              'black','white','red','blue','beige','khaki','navy','gray','olive',
              'charcoal','mint','brown','green','yellow','pink','purple']:
        name = name.replace(c, '')
    return re.sub(r'\s+', ' ', re.sub(r'[_\-/\(\)\[\]\d]',' ', name)).strip()

def dedup_name(results, products_df):
    seen, out = set(), []
    for item in results:
        if products_df is not None:
            row  = products_df[products_df['ID'] == str(item['product_id'])]
            name = row.iloc[0].get('상품명','') if not row.empty else str(item['product_id'])
        else:
            name = str(item['product_id'])
        base = _strip_color(name)
        if len(base) < 3: base = name
        if base not in seen:
            seen.add(base)
            item['display_name'] = name
            out.append(item)
    return out

def mmr_dedup(results):
    sel, sel_embs = [], []
    for item in results:
        emb  = clip_image_db[item['_db_idx']]
        norm = emb / (np.linalg.norm(emb) + 1e-8)
        if not any(np.dot(norm, s) >= MMR_THRESHOLD for s in sel_embs):
            sel.append(item)
            sel_embs.append(norm)
    return sel


# ==================== 추천 ====================

def recommend(image_path, top_k=10, min_price=5000, max_price=None):
    print(f"🔍 '{image_path}' 분석 중...\n")

    image_raw = Image.open(image_path).convert('RGB')

    print("   ✂️  배경 제거 중...")
    image_pil = remove_background(image_raw)
    print("   ✅ 완료\n")

    query_lab              = extract_query_lab(image_pil)
    feats                  = extract_query_features(image_pil)
    detected_cat, top3_cat = detect_category(feats['clip_img_emb'][0])
    col_names              = extract_main_colors(image_pil)

    print(f"   📂 카테고리  : {detected_cat}")
    print(f"      top3     : {', '.join(f'{c}({s:.3f})' for c,s in top3_cat)}")
    if col_names:
        print(f"   🖌️  주요 색상  : {', '.join(col_names[:3])}")
    print(f"\n   🎨 CLIP 디자인 (상위 5개):")
    for name, score in sorted(feats['design_scores'].items(),
                               key=lambda x: x[1], reverse=True)[:5]:
        print(f"      {name:<18}: {score:.1%}  {'█'*int(score*30)}")
    print(f"      → 주요: '{feats['top_design']}'")
    print(f"\n   📊 점수 비중  : CLIP {W_CLIP_IMAGE:.0%} | LAB색상 {W_LAB_COLOR:.0%} | ViT {W_VIT:.0%} | 디자인 {W_CLIP_DESIGN:.0%}\n")

    search_k = min(len(clip_image_db), top_k * 30)
    q_vec    = feats['clip_img_emb'].astype('float32').copy()
    faiss.normalize_L2(q_vec)
    distances, indices = faiss_index.search(q_vec, search_k)

    results = []
    for db_idx, score in zip(indices[0], distances[0]):
        row = metadata.iloc[db_idx]
        pid = str(row['product_id'])
        if row['category'] != detected_cat:
            continue
        price = name = url = None
        if products_df is not None:
            prow = products_df[products_df['ID'] == pid]
            if prow.empty: continue
            price = prow.iloc[0]['price']
            name  = prow.iloc[0].get('상품명')
            url   = prow.iloc[0].get('상품 URL')
            if pd.isna(price) or price < min_price: continue
            if max_price and price > max_price: continue
        results.append({
            'product_id'   : int(row['product_id']),
            'category'     : row['category'],
            'shopping_mall': row.get('shopping_mall', 'N/A'),
            'faiss_score'  : float(score),
            'lab_sim'      : 0.0,
            'vit_sim'      : 0.0,
            'design_sim'   : 0.0,
            'final_score'  : float(score),
            'image_path'   : row['saved_path'],
            'price'        : price,
            'name'         : name,
            'url'          : url,
            '_db_idx'      : int(db_idx),
        })

    results = dedup_name(results, products_df)
    results = mmr_dedup(results)
    results = rerank(results, feats, query_lab)

    for item in results:
        item['common_designs'] = get_common_designs(
            feats['design_probs'], item['_db_idx']
        )

    return results[:top_k], col_names, feats, detected_cat


# ==================== 출력 ====================

def print_results(results, col_names, feats, detected_cat):
    print("=" * 90)
    print(f"{'🎯 최종 추천 결과 v3':^90}")
    print("=" * 90)
    print(f"  카테고리    : {detected_cat}")
    print(f"  주요 디자인 : {feats['top_design']} ({feats['design_scores'][feats['top_design']]:.1%})")
    if col_names:
        print(f"  주요 색상   : {', '.join(col_names[:3])}")
    print("-" * 90)

    for i, item in enumerate(results, 1):
        name = item.get('display_name') or item.get('name') or f"ID {item['product_id']}"
        print(f"{i:>2}. [{item['category']}] {name}")
        if item.get('price'):
            print(f"    💰 {item['price']:,.0f}원  🏪 {item['shopping_mall']}")

        # 최종 점수 (%)
        print(f"    ⭐ 종합 유사도  : {item['final_score']*100:.2f}%")

        # 세부 점수 (%)
        print(f"    🎨 색상 유사도  : {item['lab_sim']*100:.2f}%")
        print(f"    👗 형태 유사도  : {item['vit_sim']*100:.2f}%")
        print(f"    ✨ 특징 유사도  : {item['faiss_score']*100:.2f}%")

        # CLIP 디자인 특징 퍼센티지
        db_design = clip_design_db[item['_db_idx']]
        top_designs = sorted(zip(DESIGN_NAMES, db_design), key=lambda x: x[1], reverse=True)[:5]
        design_str  = '  '.join(f"{n} {v*100:.2f}%" for n, v in top_designs if v > 0.05)
        if design_str:
            print(f"    📊 디자인 특징  : {design_str}")

        # 공통 디자인
        common = item.get('common_designs', [])
        if common:
            tags = '  '.join(f"{n}({qs*100:.2f}%↔{ds*100:.2f}%)" for n, qs, ds in common[:4])
            print(f"    🔗 공통 디자인  : {tags}")

        if item.get('url') and str(item['url']) not in ('nan', 'N/A'):
            print(f"    🌐 {item['url']}")
        print(f"    🖼️  {item['image_path']}\n")

    print("=" * 90)


# ==================== 실행 ====================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python recommend_final.py <이미지> [개수] [최소가격] [최대가격]")
        print("예시  : python recommend_final.py supreme.jpg 10")
        sys.exit()

    image_path = sys.argv[1]
    top_k      = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    min_price  = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    max_price  = int(sys.argv[4]) if len(sys.argv) > 4 else None

    results, col_names, feats, detected_cat = recommend(
        image_path, top_k=top_k, min_price=min_price, max_price=max_price
    )
    if not results:
        print("❌ 조건에 맞는 상품 없음")
    else:
        print_results(results, col_names, feats, detected_cat)
