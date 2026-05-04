import numpy as np
import pandas as pd
import faiss
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CLIP_PATH = os.path.join(BASE_DIR, "embeddings_clip_image.npy")

DALUM_PATH = os.path.join(
    BASE_DIR,
    "..",
    "vit",
    "outputs",
    "vit_output",
    "embeddings.npy"
)

META_PATH = os.path.join(
    BASE_DIR,
    "..",
    "vit",
    "outputs",
    "vit_output",
    "metadata.csv"
)

# =========================
# DB 로드 (서버 시작 시 1회)
# =========================

print("Loading recommendation DB...")

clip = np.load(CLIP_PATH)
dalum = np.load(DALUM_PATH)

metadata = pd.read_csv(META_PATH)

features = np.concatenate([clip, dalum], axis=1)

dim = features.shape[1]

faiss.normalize_L2(features)

index = faiss.IndexFlatIP(dim)
index.add(features)

print("FAISS DB loaded:", features.shape)

# =========================
# 추천
# =========================

def recommend(query_embedding, top_k=10):

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, top_k)

    results = []

    for idx, score in zip(indices[0], scores[0]):

        row = metadata.iloc[idx]

        results.append({
            "product_id": int(row["product_id"]),
            "major_category": row["major_category"],
            "middle_category": row["middle_category"],
            "image_type": row["image_type"],
            "score": float(score)
        })

    return results


# =========================
# 로컬 이미지 → Dalum embedding
# =========================

def extract_dalum_embedding(image_path):

    from vit.preprocess.utils.image_loader import load_image_from_url
    from vit.preprocess.pipeline.step1_face_judge import Step1FaceJudge
    from vit.preprocess.processors.model_processor import ModelProcessor
    from vit.preprocess.processors.product_processor import ProductProcessor
    from vit.preprocess.pipeline.segmentation_processor import SegmentationProcessor
    from vit.preprocess.color.color_extractor import ColorExtractor
    from vit.preprocess.color.color_embedding import build_color_embedding
    from vit.preprocess.material.predictor import MaterialPredictor
    from vit.preprocess.material.material_postprocessor import MaterialPostProcessor
    from vit.preprocess.utils.image_enhancer import enhance_for_material

    import cv2

    img = cv2.imread(image_path)

    # segmentation
    seg = SegmentationProcessor()
    seg_result = seg.process(img)

    # color
    color_extractor = ColorExtractor()
    colors = color_extractor.extract(seg_result)

    color_embedding = build_color_embedding(colors)

    # material
    enhanced = enhance_for_material(seg_result)

    predictor = MaterialPredictor()
    material_probs = predictor.predict(enhanced)

    post = MaterialPostProcessor()
    material_embedding = post.process(material_probs)

    embedding = np.concatenate([color_embedding, material_embedding])

    return embedding.reshape(1, -1)


# =========================
# 이미지 → 추천
# =========================

def recommend_from_image(image_path, top_k=10):

    from dupe.build_clip import extract_clip_embedding

    # CLIP
    clip_vec = extract_clip_embedding(image_path)

    # Dalum
    dalum_vec = extract_dalum_embedding(image_path)

    # concat
    query = np.concatenate([clip_vec, dalum_vec], axis=1)

    return recommend(query, top_k)