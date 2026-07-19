from fastapi import APIRouter
from app.core.responses import success_response
from app.core.exceptions import CustomException
from app.schemas.vit_schema import DupeSearchRequest, DupeSearchWithImageRequest

from dupe.dupe import recommend_from_embedding
from vit.runners.run_upload_vit import process_upload_image

router = APIRouter()


@router.post("/search")
async def search_dupe(request: DupeSearchRequest):
    """
    /vit/embedding 응답값을 그대로 body로 전달하면 듀프 제품을 반환합니다.
    """
    try:
        results, color_insufficient = recommend_from_embedding(
            clip_emb=request.clip_embedding,
            color_emb=request.embedding["color"],
            shape_emb=request.embedding.get("shape", [0.0] * 768),
            material_dict=request.embedding["material"],
            design_probs=request.clip_design_probs,
            top_k=request.top_k,
            major_category=request.major_category,
            middle_category=request.middle_category,
            lab_color=request.lab_color,
        )

        message = "유사한 색상의 제품을 충분히 찾지 못했습니다" if color_insufficient else "듀프 검색 완료"
        return success_response(
            message=message,
            data={"results": results, "color_match_insufficient": color_insufficient}
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException("INTERNAL_SERVER_ERROR")


@router.post("/dupe-search")
async def search_dupe_with_image(request: DupeSearchWithImageRequest):
    """
    S3에 업로드된 이미지 키를 받아 임베딩 추출 + 듀프 검색을 한 번에 처리합니다.
    """
    try:
        embedding_result = process_upload_image(s3_key=request.s3_key, category_hint=None)

        results, color_insufficient = recommend_from_embedding(
            clip_emb=embedding_result["clip_embedding"],
            color_emb=embedding_result["embedding"]["color"],
            shape_emb=embedding_result["embedding"]["shape"],
            material_dict=embedding_result["embedding"]["material"],
            design_probs=embedding_result["clip_design_probs"],
            top_k=request.top_k,
            major_category=embedding_result.get("category"),
            middle_category=embedding_result.get("middle_category"),
            lab_color=embedding_result.get("lab_color"),
        )

        message = "유사한 색상의 제품을 충분히 찾지 못했습니다" if color_insufficient else "듀프 검색 완료"
        return success_response(
            message=message,
            data={
                "results": results,
                "color_match_insufficient": color_insufficient,
                "style": embedding_result["style"],
                "category": embedding_result["category"],
                "meta": embedding_result["meta"],
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException("INTERNAL_SERVER_ERROR")