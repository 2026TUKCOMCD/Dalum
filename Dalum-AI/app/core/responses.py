def success_response(message: str, data: dict):
    return {
        "resultType": "SUCCESS",
        "code": 200,
        "message": message,
        "data": data
    }