from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

from recommender.styling_engine import DEFAULT_SCORE_THRESHOLD, StylingRecommender

router = APIRouter()

recommender = StylingRecommender()


class InputItem(BaseModel):
    material_vector: List[float]
    dominant_colors: Optional[List[Dict[str, Any]]] = None  # [{"hex": "#RRGGBB", "ratio": 0.6}, ...]
    style:           Optional[str] = None                   # casual | formal | sporty | street | vintage | american_casual
    category:        str


class CandidateItem(BaseModel):
    id:              Any
    category:        str
    style:           Optional[str] = None
    material_vector: List[float]
    dominant_colors: Optional[List[Dict[str, Any]]] = None
    metadata:        Optional[Dict[str, Any]] = None


class RecommendRequest(BaseModel):
    input:          InputItem
    candidates:     List[CandidateItem]
    top_k:          int   = 3
    score_threshold: float = DEFAULT_SCORE_THRESHOLD


@router.post("/recommend")
def recommend(req: RecommendRequest):
    return recommender.get_recommendations(
        input_material_vector=req.input.material_vector,
        input_category=req.input.category,
        candidates=[c.model_dump() for c in req.candidates],
        top_k=req.top_k,
        input_dominant_colors=req.input.dominant_colors,
        input_style=req.input.style,
        score_threshold=req.score_threshold,
    )
