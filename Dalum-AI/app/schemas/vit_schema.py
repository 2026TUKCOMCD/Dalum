from pydantic import BaseModel

class VitRequest(BaseModel):
    s3Key: str