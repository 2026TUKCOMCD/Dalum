# 라우터 모음
from fastapi import APIRouter
import urllib.parse

from vit.runners.run_upload_vit import process_upload_image
from app.schemas.vit_schema import VitRequest
from app.core.responses import success_response
from app.core.exceptions import CustomException

router = APIRouter()


@router.post("/embedding")
def create_embedding(request: VitRequest):

    try:
        # S3Key 정규화
        decoded_key = urllib.parse.unquote(request.s3Key)
        decoded_key = decoded_key.replace("+", " ")

        result = process_upload_image(
            s3_key=decoded_key,
            category_hint=None
        )

        return success_response(
            message="임베딩 생성 완료",
            data=result
        )

    except ValueError:
        raise CustomException("IMAGE_NOT_FOUND")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise CustomException("INTERNAL_SERVER_ERROR")