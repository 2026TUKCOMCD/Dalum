from fastapi import HTTPException
from app.core.error_codes import ERROR_CODES


class CustomException(HTTPException):
    def __init__(self, error_code: str):

        error_info = ERROR_CODES.get(error_code)

        if not error_info:
            error_info = ERROR_CODES["INTERNAL_SERVER_ERROR"]
            error_code = "INTERNAL_SERVER_ERROR"

        super().__init__(
            status_code=error_info["status"],
            detail={
                "resultType": "FAIL",
                "code": error_info["status"],
                "errorCode": error_code,
                "reason": error_info["message"],
                "data": None
            }
        )