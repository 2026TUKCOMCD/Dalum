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
                "product_id"    : int(item["product_id"]),
                "name"          : str(item.get("display_name") or item.get("name") or ""),
                "category"      : str(item["category"]),
                "shopping_mall" : str(item["shopping_mall"]),
                "price"         : float(item["price"]) if item.get("price") is not None else None,
                "url"           : str(item.get("url")) if item.get("url") else None,
                "image_path"    : str(item.get("image_path")) if item.get("image_path") else None,
                "final_score"   : float(item["final_score"]),
                "lab_sim"       : float(item["lab_sim"]),
                "vit_sim"       : float(item["vit_sim"]),
                "faiss_score"   : float(item["faiss_score"]),
                "common_designs": [(str(n), float(q), float(d)) for n, q, d in item.get("common_designs", [])],
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