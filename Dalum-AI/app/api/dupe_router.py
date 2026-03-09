from fastapi import APIRouter, UploadFile, File
from app.core.responses import success_response
from app.core.exceptions import CustomException
import tempfile, os, sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../..'))
from dupe.dupe import recommend

router = APIRouter()

@router.post("/search")
async def search_dupe(file: UploadFile = File(...), top_k: int = 10):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        results, col_names, feats, detected_cat = recommend(
            tmp_path, top_k=top_k
        )
        os.unlink(tmp_path)

        output = []
        for item in results:
            output.append({
                "product_id"    : item["product_id"],
                "name"          : item.get("display_name") or item.get("name"),
                "category"      : item["category"],
                "shopping_mall" : item["shopping_mall"],
                "price"         : item.get("price"),
                "url"           : item.get("url"),
                "image_path"    : item.get("image_path"),
                "final_score"   : item["final_score"],
                "lab_sim"       : item["lab_sim"],
                "vit_sim"       : item["vit_sim"],
                "faiss_score"   : item["faiss_score"],
                "common_designs": item.get("common_designs", []),
            })

        return success_response(
            message="듀프 검색 완료",
            data={
                "results"    : output,
                "colors"     : col_names,
                "top_design" : feats["top_design"],
                "category"   : detected_cat,
            }
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException("INTERNAL_SERVER_ERROR")