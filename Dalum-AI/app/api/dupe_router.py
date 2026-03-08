from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile, os
from app.core.responses import success_response
from app.core.exceptions import CustomException

# dupe.py에서 recommend 함수 import
import sys
sys.path.append(os.path.expanduser('~'))
from dupe import recommend

router = APIRouter()

@router.post("/search")
async def search_dupe(file: UploadFile = File(...), top_k: int = 10):
    try:
        # 업로드된 이미지 임시 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        results, col_names, feats, detected_cat = recommend(
            tmp_path, top_k=top_k
        )
        os.unlink(tmp_path)

        # 결과 직렬화
        output = []
        for item in results:
            output.append({
                "product_id"   : item["product_id"],
                "name"         : item.get("display_name") or item.get("name"),
                "category"     : item["category"],
                "shopping_mall": item["shopping_mall"],
                "price"        : item.get("price"),
                "url"          : item.get("url"),
                "image_path"   : item.get("image_path"),
                "final_score"  : item["final_score"],
                "lab_sim"      : item["lab_sim"],
                "vit_sim"      : item["vit_sim"],
                "faiss_score"  : item["faiss_score"],
                "common_designs": item.get("common_designs", []),
            })

        return success_response(
            message="듀프 검색 완료",
            data={
                "results"      : output,
                "colors"       : col_names,
                "top_design"   : feats["top_design"],
                "category"     : detected_cat,
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException("INTERNAL_SERVER_ERROR")